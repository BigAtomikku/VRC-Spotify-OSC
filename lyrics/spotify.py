from providers import Spotify


class SpotifyLyrics:
    def __init__(self, sp_dc):
        self.Spotify = Spotify(sp_dc)

    def get_lyrics(self, playback):
        lyrics_data = self.Spotify.get_lyrics(playback.id)
        if not lyrics_data:
            return False

        lines = lyrics_data['lyrics']['lines']
        return {int(line['startTimeMs']): line['words'] for line in lines}
