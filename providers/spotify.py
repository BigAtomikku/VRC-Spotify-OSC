# TOTP class taken from votify by glomatico (https://github.com/glomatico/votify)
# Licensed under MIT License

import math
import hmac
import hashlib
import spotipy
import requests


class InvalidSpDcCookie(Exception):
    pass


class TOTP:
    def __init__(self) -> None:
        # dumped directly from the object, after all decryptions
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

        return str(binary % (10**self.digits)).zfill(self.digits)


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
        self.sp = spotipy.Spotify(auth=self._fetch_access_token())

    def _fetch_access_token(self):
        try:
            server_time_response = self.session.get("https://open.spotify.com/server-time")
            server_time = server_time_response.json()["serverTime"] * 1000
            totp = self.totp.generate(timestamp=int(server_time))
            token_url = (f"https://open.spotify.com/get_access_token?reason=transport&productType=web_player&totp="
                         f"{totp}&totpVer={self.totp.version}&ts={int(server_time)}")

            response = self.session.get(token_url)
            response.raise_for_status()

            token_data = response.json()
            token = token_data.get("accessToken")

            if not token.startswith("BQ"):
                return self._fetch_access_token()

            self.session.headers["Authorization"] = f"Bearer {token}"
            return token

        except requests.RequestException as e:
            raise InvalidSpDcCookie(f"Failed to get access token {e}")

    def current_playback(self):
        return self.sp.current_playback()

    def get_lyrics(self, track_id):
        url = f"https://spclient.wg.spotify.com/color-lyrics/v2/track/{track_id}"
        params = {"format": "json", "market": "from_token"}

        response = self.session.get(url, params=params)

        return response.json() if response.status_code == 200 else None
