import time
import ctypes
import syrics.exceptions
from colorama import Fore
from syrics.api import Spotify
from pythonosc.udp_client import SimpleUDPClient


def disable_quick_edit_mode():
    stdin_handle = ctypes.windll.kernel32.GetStdHandle(-10)
    if stdin_handle is None or stdin_handle == ctypes.c_void_p(-1).value:
        return False

    mode = ctypes.c_ulong(0)
    if not ctypes.windll.kernel32.GetConsoleMode(stdin_handle, ctypes.byref(mode)):
        return False

    new_mode = ctypes.c_ulong(mode.value & ~0x0040)

    if not ctypes.windll.kernel32.SetConsoleMode(stdin_handle, new_mode):
        return False

    return True


if not disable_quick_edit_mode():
    print(Fore.RED + "Failed to disable Quick Edit mode")


while True:
    try:
        sp = Spotify(input(Fore.RESET + "Enter website sp_dc cookie value: "))
        break
    except syrics.exceptions.NotValidSp_Dc:
        print(Fore.RED + "sp_dc provided is invalid, please check it again!")


ip = "127.0.0.1"
port = 9000
client = SimpleUDPClient(ip, port)  # Create client
print(Fore.RESET + "Connected to Client")


class CurrentSong:
    def __init__(self, data):
        try:
            self.uri = data['item']['id']
        except TypeError:
            return
        self.name = data['item']['name']
        self.artist = data['item']['artists'][0]['name']
        self.progress = data['progress_ms']
        self.playing = data['is_playing']


song = ''
lyrics = []
no_lyrics = False
spaces = ' ' * 50
last_line_index = -1  # Reset the last printed line index

while True:
    current_song_data = sp.get_current_song()
    current_song = CurrentSong(current_song_data)

    try:

        if current_song.name + current_song.artist != song:
            no_lyrics = False
            print('\r' + spaces)
            print(Fore.MAGENTA + "Now playing: " + current_song.name + " by " + current_song.artist + spaces)
            client.send_message("/chatbox/input", ["Now playing: " + current_song.name + " by " +
                                                   current_song.artist, True, False])  # Send message
            song = current_song.name + current_song.artist
            time.sleep(3)
            lyrics = sp.get_lyrics(current_song.uri)

            if lyrics:
                lyrics = lyrics['lyrics']['lines']
                last_line_index = -1
            else:
                no_lyrics = True
                song = current_song.name + current_song.artist
                print(Fore.YELLOW + "Lyrics for this track are not available on spotify")

        if current_song.playing:
            if not no_lyrics:
                progress_ms = current_song.progress
                for i, line in enumerate(lyrics):
                    if int(progress_ms - 150 <= int(line['startTimeMs']) <= int(progress_ms + 150)):
                        if i != last_line_index:
                            time.sleep(0.45)
                            print(Fore.RESET + "\rLyrics: " + line['words'] + spaces, end='')
                            client.send_message("/chatbox/input", [line['words'], True, False])  # Send message
                            last_line_index = i

            else:
                time.sleep(5)
        else:
            print(Fore.RESET + "\rPaused" + spaces, end='')
            time.sleep(1)

    except AttributeError:
        continue
