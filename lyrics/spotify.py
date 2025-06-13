# TOTP class taken from votify by glomatico (https://github.com/glomatico/votify)
# Licensed under MIT License

import time
import math
import hmac
import hashlib
import spotipy
import requests


class SpotifyAuthError(Exception):
    """Raised when we fail to fetch or parse a Spotify access token."""
    pass


class TOTP:
    def __init__(self) -> None:
        self.secret = b"5507145853487499592248630329347"
        self.version = 5
        self.period = 30
        self.digits = 6

    def generate(self, timestamp: int) -> str:
        counter = math.floor(timestamp / 1000 / self.period)
        counter_bytes = counter.to_bytes(8, byteorder="big")

        h = hmac.new(self.secret, counter_bytes, hashlib.sha1)
        hmac_result = h.digest()

        offset = hmac_result[-1] & 0x0F
        binary = (
                (hmac_result[offset] & 0x7F) << 24
                | (hmac_result[offset + 1] & 0xFF) << 16
                | (hmac_result[offset + 2] & 0xFF) << 8
                | (hmac_result[offset + 3] & 0xFF)
        )

        return str(binary % (10 ** self.digits)).zfill(self.digits)


class Spotify:
    def __init__(self, sp_dc_cookie):
        if not sp_dc_cookie:
            raise ValueError("Missing sp_dc cookie")

        self.session = requests.Session()
        self.session.cookies.set('sp_dc', sp_dc_cookie)
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0",
            "App-Platform": "WebPlayer"
        })
        self.totp = TOTP()
        self.token = None
        self._fetch_access_token()
        self.sp = spotipy.Spotify(self.token)

    def _fetch_access_token(self):
        now_ms = int(time.time() * 1000)
        totp = self.totp.generate(timestamp=now_ms)

        params = {
            "reason": "transport",
            "productType": "web-player",
            "totp": totp,
            "totpServer": totp,
            "totpVer": str(self.totp.version),
        }

        response = self.session.get("https://open.spotify.com/api/token", params=params)
        token = response.json().get("accessToken")
        if not token:
            raise SpotifyAuthError(f"Invalid sp_dc cookie")

        self.token = response.json()['accessToken']
        self.session.headers['Authorization'] = f"Bearer {self.token}"

    def get_lyrics(self, track_id):
        url = f"https://spclient.wg.spotify.com/color-lyrics/v2/track/{track_id}"
        params = {"format": "json", "market": "from_token"}

        response = self.session.get(url, params=params)

        return response.json() if response.status_code == 200 else None


class SpotifyLyrics:
    def __init__(self, sp_dc):
        self.Spotify = Spotify(sp_dc)

    def get_lyrics(self, playback):
        lyrics_data = self.Spotify.get_lyrics(playback.id)
        if not lyrics_data:
            return False

        lines = lyrics_data['lyrics']['lines']
        return {int(line['startTimeMs']): line['words'] for line in lines}
