from lrclib import LrcLibAPI


def lrc_to_dictionary(lrc):
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


class LRCLibLyrics:
    def __init__(self):
        self.lyrics_api = LrcLibAPI(user_agent="VRC-Lyrics")

    def get_lyrics(self, playback):
        duration = playback.duration_ms / 1000
        words = playback.name.split()

        for wc in range(len(words), 0, -1):
            title = ' '.join(words[:wc])
            for artist in playback.artists:
                results = self.lyrics_api.search_lyrics(track_name=title, artist_name=artist['name'])
                filtered = [r for r in results if r.synced_lyrics and abs(r.duration - duration) <= 3]
                if filtered:
                    return lrc_to_dictionary(filtered[0].synced_lyrics)
