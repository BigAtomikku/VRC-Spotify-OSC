import asyncio
import spotipy
from lrclib import LrcLibAPI
from providers import Spotify, InvalidSpDcCookie


class Playback:
    def __init__(self, update_track_info):
        self.spotify = None
        self.id = None
        self.name = None
        self.artists = []
        self.progress_ms = 0
        self.duration_ms = 0
        self.is_playing = False
        self.album_cover = None
        self.lyrics = None
        self.update_track_info = update_track_info
        self.lyrics_provider = None

        if self.lyrics_provider == "LRCLibAPI":
            self.lyrics_api = LrcLibAPI(user_agent="VRC-Lyrics")

    def fetch_playback(self):
        data = self.spotify.current_playback()

        if data and data['item']:
            self.id = data['item']['id']
            self.name = data['item']['name']
            self.artists = data['item']['artists']
            self.progress_ms = data['progress_ms']
            self.duration_ms = data['item']['duration_ms']
            self.is_playing = data['is_playing']
            self.album_cover = data['item']['album']['images'][0]['url']
            return True
        return False

    def has_changed_track(self, previous_id):
        return self.id != previous_id

    def is_instrumental(self):
        return "instrumental" in self.name.lower()

    def get_lyrics(self):
        match self.lyrics_provider:
            case "Spotify":
                return self.get_lyrics_spotify()
            case "LRCLibAPI":
                return self.get_lyrics_lrclib()

    def get_lyrics_lrclib(self):
        self.lyrics = None
        track_duration = self.duration_ms / 1000
        artists = self.artists
        words = self.name.split()

        for word_count in range(len(words), 0, -1):
            track_name = ' '.join(words[:word_count])

            for artist in artists:
                print(f"Searching {track_name} by {artist['name']} with duration {track_duration}s via LRCLib")
                results = self.lyrics_api.search_lyrics(track_name=track_name, artist_name=artist['name'])
                filtered_results = [r for r in results if r.synced_lyrics and abs(r.duration - track_duration) <= 3]

                if filtered_results:
                    self.lrc_to_dictionary(filtered_results[0].synced_lyrics)
                    return True

        return False

    def get_lyrics_spotify(self):
        lyrics_data = self.spotify.get_lyrics(self.id)

        if not lyrics_data:
            return False

        lines = lyrics_data['lyrics']['lines']
        lyrics_dictionary = {
            int(line['startTimeMs']): line['words']
            for line in lines
        }

        self.lyrics = lyrics_dictionary
        return True

    def lrc_to_dictionary(self, lrc):
        lines = lrc.strip().split('\n')
        lrc_dict = {}

        for line in lines:
            timestamp, lyric = line.split(']', 1)
            timestamp = timestamp[1:]
            lyric = lyric.strip()

            minutes, seconds = timestamp.split(':')
            total_ms = int(minutes) * 60 * 1000 + float(seconds) * 1000

            lrc_dict[int(total_ms)] = lyric

        self.lyrics = lrc_dict


async def poll_playback(playback, song_data_queue, running):
    track_id = None
    playing = None

    while running.is_set():
        if playback.fetch_playback():
            playback.update_track_info(progress=playback.progress_ms, duration=playback.duration_ms)

            if playback.has_changed_track(track_id):
                playback.lyrics = None
                playback.update_track_info(title=playback.name,
                                           artist=", ".join(artist['name'] for artist in playback.artists),
                                           album_art=playback.album_cover, lyric="")
                song_data_queue.put({'type': 'song_update', 'playback': playback})
                track_id = playback.id

                if playback.is_instrumental() or not playback.get_lyrics():
                    playback.update_track_info(lyric="Lyrics for this track are not available")

            if playing is None or playback.is_playing != playing:
                song_data_queue.put({'type': 'is_playing', 'is_playing': playback.is_playing})
                playing = playback.is_playing
        else:
            print("Failed to fetch playback info. Retrying...")

        await asyncio.sleep(0.6)


async def lyric_update_loop(playback, song_data_queue, running):
    previous_position = 0
    previous_key = None
    previous_track_id = None

    def is_scrubbed_backwards():
        return playback.progress_ms < previous_position - 1000 and playback.progress_ms < min(playback.lyrics.keys())

    while running.is_set():
        if playback.lyrics:
            if playback.id == previous_track_id and is_scrubbed_backwards():
                song_data_queue.put({'type': 'lyric_update', 'lyric': ""})

            current_key = max((k for k in playback.lyrics.keys() if k <= playback.progress_ms), default=None)

            if current_key is not None and current_key != previous_key:
                lyric = playback.lyrics[current_key]
                if lyric is not None:
                    playback.update_track_info(lyric=lyric)
                    song_data_queue.put({'type': 'lyric_update', 'lyric': lyric})
                previous_key = current_key

            previous_position = playback.progress_ms
            previous_track_id = playback.id

        await asyncio.sleep(0.1)


def connect_to_lrc_lib(client_id):
    lrclib_api = LrcLibAPI(user_agent="VRC-Lyrics/2.5.0")
    redirect_uri = "http://127.0.0.1:5000/callback"
    scope = "user-read-playback-state"

    auth_manager = spotipy.SpotifyPKCE(client_id=client_id, redirect_uri=redirect_uri, scope=scope)
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    return lrclib_api, spotify


async def lrc_loop(provider, key, song_data_queue, running, update_track_info):
    playback = Playback(update_track_info=update_track_info)

    try:
        match provider:
            case "Spotify":
                print("Connecting to Spotify")
                playback.spotify = Spotify(key)
                playback.lyrics_provider = "Spotify"

            case "LRCLibAPI":
                print("Connecting to LRCLibAPI")
                lrclib_api, spotify = connect_to_lrc_lib(key)
                playback.spotify = spotify
                playback.lyrics_api = lrclib_api
                playback.lyrics_provider = "LRCLibAPI"

        await asyncio.gather(
            poll_playback(playback, song_data_queue, running),
            lyric_update_loop(playback, song_data_queue, running)
        )

    except InvalidSpDcCookie as e:
        print(f"[ERROR] Invalid sp_dc cookie: {e}")
        playback.update_track_info(lyric="Invalid SP_DC cookie provided")
        return

    print("[LRC Loop] Exiting cleanly")
