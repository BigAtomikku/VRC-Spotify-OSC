from dataclasses import dataclass
from playback.base import BasePlayback


@dataclass
class SongUpdate:
    playback: BasePlayback
    type: str = "song_update"

    def __repr__(self):
        return f"[{self.__class__.__name__}] {self.playback.name} - {self.playback.artists[0]['name']}"


@dataclass
class LyricUpdate:
    lyric: str
    type: str = "lyric_update"

    def __repr__(self):
        return f"[{self.__class__.__name__}] {self.lyric}"


@dataclass
class IsPlayingUpdate:
    is_playing: bool
    type: str = "is_playing"

    def __repr__(self):
        return f"[{self.__class__.__name__}] {self.is_playing}"
