import time
import spotipy
import hashlib
import requests
from pyotp import TOTP


class InvalidSpDcCookie(Exception):
    pass


def generate_totp():
    raw_bytes = [12, 56, 76, 33, 88, 44, 88, 33, 78, 78, 11, 66, 22, 22, 55, 69, 54]
    deobfuscated = [(val ^ (i % 33 + 9)) for i, val in enumerate(raw_bytes)]

    byte_str = bytes(''.join(map(str, deobfuscated)), 'utf-8')
    hex_str = ''.join(format(b, '02x') for b in byte_str)

    charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
    secret_bytes = bytes.fromhex(hex_str)

    bits_collected = 0
    current_byte = 0
    secret = ""

    for byte in secret_bytes:
        current_byte = (current_byte << 8) | byte
        bits_collected += 8
        while bits_collected >= 5:
            bits_collected -= 5
            secret += charset[(current_byte >> bits_collected) & 31]

    if bits_collected > 0:
        secret += charset[(current_byte << (5 - bits_collected)) & 31]

    return TOTP(secret, digits=6, digest=hashlib.sha1, interval=30).now()


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
        self.sp = spotipy.Spotify(auth=self._fetch_access_token())

    def _fetch_access_token(self):
        try:
            totp = generate_totp()
            timestamp = int(time.time())
            token_url = (f"https://open.spotify.com/get_access_token?reason=transport&productType=web_player&totp="
                         f"{totp}&totpVer=5&ts={timestamp}")

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
