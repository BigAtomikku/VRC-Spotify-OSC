import spotipy
from playback import BasePlayback

redirect_uri = "http://127.0.0.1:5000/callback"
scope = "user-read-playback-state"


class SpotifyPlayback(BasePlayback):
    def __init__(self, client_id, lyrics):
        super().__init__()
        auth_manager = spotipy.SpotifyPKCE(client_id=client_id, redirect_uri=redirect_uri, scope=scope)
        self.spotify = spotipy.Spotify(auth_manager=auth_manager)
        self.id = None
        self.lyrics_provider = lyrics
        self.album_cover = None
        self._last_id = None

    async def fetch_playback(self):
        data = self.spotify.current_playback()
        if not data or not data['item']:
            return False

        self.id = data['item']['id']
        self.name = data['item']['name']
        self.artists = data['item']['artists']
        self.progress_ms = data['progress_ms']
        self.duration_ms = data['item']['duration_ms']
        self.is_playing = data['is_playing']
        images = data['item']['album']['images']
        self.album_cover = images[0]['url'] if images else None

        if self.lyrics_provider:
            if (self.id, self.name, self.artists) != (self._last_id, self._last_name, self._last_artists):
                self.lyrics = self.lyrics_provider.get_lyrics(self)

            self._update_current_lyric()

        return True

    def has_changed_track(self):
        result = (self.id, self.name, self.artists) != (self._last_id, self._last_name, self._last_artists)
        if result:
            self.current_lyric, self._last_lyric_key, self.current_lyric_key = None, None, None
            self._last_id = self.id
            self._last_name = self.name
            self._last_artists = self.artists
        return result
