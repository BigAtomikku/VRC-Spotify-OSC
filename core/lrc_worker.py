import config
import asyncio
from lyrics import LRCLibLyrics, SpotifyLyrics, SpotifyAuthError
from playback import SpotifyPlayback, WindowsPlayback
from .messages import LyricUpdate, SongUpdate, IsPlayingUpdate


async def poll_playback(playback, song_data_queue, running, handlers):
    previous_position = 0
    previous_key = None

    while running.is_set():
        previous_is_playing = playback.is_playing
        fetch_success = await playback.fetch_playback()
        if not fetch_success:
            await asyncio.sleep(1)
            continue

        handlers.progress(progress=playback.progress_ms, duration=playback.duration_ms)

        if playback.has_changed_track():
            handle_track_change(playback, song_data_queue, handlers)
            previous_position = playback.progress_ms
            previous_key = playback.current_lyric_key

        else:
            if playback.is_playing != previous_is_playing:
                song_data_queue.put(IsPlayingUpdate(is_playing=playback.is_playing))

            if playback.lyrics:
                previous_key = update_lyrics(playback, previous_position, previous_key, song_data_queue, handlers)
                previous_position = playback.progress_ms

        await asyncio.sleep(1)


def handle_track_change(playback, song_data_queue, handlers):
    handlers.track_info(title=playback.name,
                        artist=", ".join(artist['name'] for artist in playback.artists),
                        album_art=getattr(playback, "album_cover", None))
    handlers.lyric(lyric=playback.current_lyric)
    song_data_queue.put(SongUpdate(playback=playback))

    if not playback.lyrics_provider:
        handlers.lyric(lyric="No lyric provider selected in settings")
        return

    if playback.is_instrumental() or not playback.lyrics:
        handlers.lyric(lyric="Lyrics for this track are not available")


def update_lyrics(playback, previous_position, previous_key, song_data_queue, handlers):
    current_key = playback.current_lyric_key

    if playback.progress_ms < previous_position - 1000 and current_key is None:
        song_data_queue.put(LyricUpdate(lyric=""))
        handlers.lyric(lyric="")
        return None

    if current_key is not None and current_key != previous_key:
        lyric = playback.lyrics[current_key]
        if lyric is not None:
            handlers.lyric(lyric=lyric)
            song_data_queue.put(LyricUpdate(lyric=lyric))
        return current_key

    return previous_key


async def lrc(song_data_queue, running, handlers):
    playback, lyrics = None, None
    playback_provider = config.get('playback_provider')
    lyric_provider = config.get('lyric_provider')

    match lyric_provider:
        case "Spotify":
            try:
                sp_dc = config.get('sp_dc')
                lyrics = SpotifyLyrics(sp_dc=sp_dc)
            except SpotifyAuthError:
                handlers.error("Invalid sp_dc cookie")

        case "LRCLib":
            lyrics = LRCLibLyrics()

    match playback_provider:
        case "Spotify":
            client_id = config.get('client_id')
            playback = SpotifyPlayback(client_id=client_id, lyrics=lyrics)
        case "Windows":
            playback = WindowsPlayback(lyrics=lyrics)

    if playback:
        await poll_playback(playback, song_data_queue, running, handlers)
