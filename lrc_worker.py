import asyncio
import requests
from lrclib import LrcLibAPI
from spotipy import Spotify, SpotifyPKCE


class Playback:
    def __init__(self, spotify, update_track_info):
        self.spotify = spotify
        self.id = None
        self.name = None
        self.artists = []
        self.progress_ms = 0
        self.duration_ms = 0
        self.is_playing = False
        self.album_cover = None
        self.lyrics = None
        self.update_track_info = update_track_info

    def fetch_playback(self):
        try:
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
        except requests.exceptions.ReadTimeout:
            print("Request timed out")
            return False

    def has_changed_track(self, previous_id):
        return self.id != previous_id

    def is_instrumental(self):
        return "instrumental" in self.name.lower()

    def get_lyrics(self, lrclib_api):
        self.lyrics = None
        track_duration = self.duration_ms / 1000
        artists = self.artists
        words = self.name.split()

        for word_count in range(len(words), 0, -1):
            track_name = ' '.join(words[:word_count])

            for artist in artists:
                print(f"Searching {track_name} by {artist['name']} with duration {track_duration}s via LRCLib")
                results = lrclib_api.search_lyrics(track_name=track_name, artist_name=artist['name'])
                filtered_results = [r for r in results if r.synced_lyrics and abs(r.duration - track_duration) <= 3]

                if filtered_results:
                    self.lyrics = lyrics_to_dict(filtered_results[0].synced_lyrics)
                    return True

        return False

    def current_lyric(self, user_time):
        key = max((k for k in self.lyrics.keys() if k < user_time), default=None)
        return self.lyrics.get(key)


def lyrics_to_dict(lrc):
    lines = lrc.strip().split('\n')
    lrc_dict = {}

    for line in lines:
        timestamp, lyric = line.split(']', 1)
        timestamp = timestamp[1:]
        lyric = lyric.strip()

        minutes, seconds = timestamp.split(':')
        total_ms = int(minutes) * 60 * 1000 + float(seconds) * 1000

        lrc_dict[int(total_ms)] = lyric

    return lrc_dict


async def poll_playback(playback, lrclib_api, song_data_queue, running):
    track_id = None
    playing = None

    while running.is_set():
        if playback.fetch_playback():
            playback.update_track_info(progress=playback.progress_ms, duration=playback.duration_ms)

            if playback.has_changed_track(track_id):
                playback.update_track_info(title=playback.name,
                                           artist=", ".join(artist['name'] for artist in playback.artists),
                                           album_art=playback.album_cover, lyric="")
                song_data_queue.put({'type': 'song_update', 'playback': playback})
                track_id = playback.id

                if playback.is_instrumental() or not playback.get_lyrics(lrclib_api):
                    playback.update_track_info(lyric="Lyrics for this track are not available")

            if playing is None or playback.is_playing != playing:
                song_data_queue.put({'type': 'is_playing', 'is_playing': playback.is_playing})
                playing = playback.is_playing
        else:
            print("Failed to fetch playback info. Retrying...")

        await asyncio.sleep(0.6)


async def lyric_update_loop(playback, song_data_queue, running):
    previous_position = 0
    previous_lyric = None

    while running.is_set():
        if playback.lyrics:
            if playback.progress_ms < previous_position - 1000 and playback.progress_ms < min(playback.lyrics.keys()):
                song_data_queue.put({'type': 'lyric_update', 'lyric': ""})

            previous_position = playback.progress_ms
            lyric = playback.current_lyric(playback.progress_ms)

            if lyric != previous_lyric:
                previous_lyric = lyric
                if lyric is not None:
                    playback.update_track_info(lyric=lyric)
                    song_data_queue.put({'type': 'lyric_update', 'lyric': lyric})

        await asyncio.sleep(0.1)


async def lrc_loop(client_id, song_data_queue, running, update_track_info):
    lrclib_api = LrcLibAPI(user_agent="VRC-Spotify-OSC/2.1.5")
    redirect_uri = "http://127.0.0.1:5000/callback"
    scope = "user-read-playback-state"

    auth_manager = SpotifyPKCE(client_id=client_id, redirect_uri=redirect_uri, scope=scope)
    spotify = Spotify(auth_manager=auth_manager)

    playback = Playback(spotify, update_track_info)

    await asyncio.gather(
        poll_playback(playback, lrclib_api, song_data_queue, running),
        lyric_update_loop(playback, song_data_queue, running)
    )

    print("[LRC Loop] Exiting cleanly")
