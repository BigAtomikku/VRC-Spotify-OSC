import time
from lrclib import LrcLibAPI
from spotipy import Spotify, SpotifyPKCE


class LRCHandler:
    def __init__(self):
        self.lyrics = None
        self.previous_lyric = ""
        self.previous_position = 0

    def current_lyric(self, user_time):
        key = max((k for k in self.lyrics.keys() if k < user_time), default=None)
        return self.lyrics.get(key)

    def update_lyric(self, song_data_queue, user_time):
        if self.previous_position > 0 and user_time < self.previous_position - 1000:
            self.previous_lyric = ""
            self.previous_position = user_time
            song_data_queue.put({'type': 'lyric_update', 'lyric': ""})

        self.previous_position = user_time
        lyric = self.current_lyric(user_time)

        if lyric != self.previous_lyric:
            self.previous_lyric = lyric
            if lyric is None:
                song_data_queue.put({'type': 'lyric_update', 'lyric': ""})
            else:
                song_data_queue.put({'type': 'lyric_update', 'lyric': lyric})

    def get_lyrics(self, song_data_queue, playback, lrclib_api):
        self.lyrics = None
        original_track_name = playback['item']['name']
        track_duration = playback['item']['duration_ms'] / 1000
        artists = playback['item']['artists']

        words = original_track_name.split()

        for word_count in range(len(words), 0, -1):
            track_name = ' '.join(words[:word_count])

            for artist in artists:
                print(f"Searching {track_name} by {artist['name']} with duration {track_duration}s via LRCLib")
                results = lrclib_api.search_lyrics(track_name=track_name, artist_name=artist['name'])
                filtered_results = [r for r in results if r.synced_lyrics and abs(r.duration - track_duration) <= 3]

                if filtered_results:
                    self.lyrics = lyrics_to_dict(filtered_results[0].synced_lyrics)
                    song_data_queue.put({'type': 'lyric_update', 'lyric': ""})
                    return
        song_data_queue.put({'type': 'lyric_update', 'lyric': None})


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


def lrc_thread(client_id, song_data_queue, running):
    lrclib_api = LrcLibAPI(user_agent="VRC-Spotify-OSC/2.1.5")
    redirect_uri = "http://127.0.0.1:5000/callback"
    scope = "user-read-playback-state"

    auth_manager = SpotifyPKCE(client_id=client_id, redirect_uri=redirect_uri, scope=scope)
    spotify = Spotify(auth_manager=auth_manager)

    last_track = ""
    playing = None
    lrc_handler = LRCHandler()

    while running.is_set():
        playback = spotify.current_playback()

        if not playback:
            time.sleep(1)
            continue

        current_track = playback["item"]["id"]

        if current_track != last_track:
            song_data_queue.put({'type': 'song_update', 'playback': playback['item']})
            lrc_handler.previous_position = 0
            last_track = current_track

            if "instrumental" in playback["item"]["name"].lower():
                song_data_queue.put({'type': 'lyric_update', 'lyric': None})
            else:
                lrc_handler.get_lyrics(song_data_queue, playback, lrclib_api)

        is_playing = playback["is_playing"]

        if playing is None or is_playing != playing:
            song_data_queue.put({'type': 'is_playing', 'is_playing': is_playing})

            if is_playing and lrc_handler.previous_lyric:
                song_data_queue.put({'type': 'lyric_update', 'lyric': lrc_handler.previous_lyric})

            playing = is_playing

        if lrc_handler.lyrics and is_playing:
            user_time = playback['progress_ms']
            lrc_handler.update_lyric(song_data_queue, user_time)

        time.sleep(0.5)
