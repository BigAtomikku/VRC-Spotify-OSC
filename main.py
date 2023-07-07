import time
import ctypes
import syrics.exceptions
from colorama import Fore
from syrics.api import Spotify
from pythonosc.udp_client import SimpleUDPClient


def disable_quick_edit_mode():
    # Get the console's standard input handle
    stdin_handle = ctypes.windll.kernel32.GetStdHandle(-10)
    if stdin_handle is None or stdin_handle == ctypes.c_void_p(-1).value:
        return False

    # Get the current console mode
    mode = ctypes.c_ulong(0)
    if not ctypes.windll.kernel32.GetConsoleMode(stdin_handle, ctypes.byref(mode)):
        return False

    # Clear the Quick Edit bit (bitmask with 0x0040)
    new_mode = ctypes.c_ulong(mode.value & ~0x0040)

    # Set the new console mode
    if not ctypes.windll.kernel32.SetConsoleMode(stdin_handle, new_mode):
        return False

    return True


# Use the function at the start of your script
if not disable_quick_edit_mode():
    print(Fore.RED + "Failed to disable Quick Edit mode")


while True:
    try:
        sp = Spotify(input(Fore.BLUE + "Enter website sp_dc cookie value: "))
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
last_line_index = -1
no_lyrics = False
spaces = ' ' * 50

while True:
    current_song_data = sp.get_current_song()
    current_song = CurrentSong(current_song_data)

    try:

        if current_song.playing:
            if current_song.name + current_song.artist != song:
                no_lyrics = False
                print(Fore.MAGENTA + "\rNow playing: " + current_song.name + " by " + current_song.artist + spaces)
                client.send_message("/chatbox/input", ["Now playing: " + current_song.name + " by " + current_song.artist, True, False])  # Send message
                song = current_song.name + current_song.artist
                lyrics = sp.get_lyrics(current_song.uri)['lyrics']['lines']
                last_line_index = -1  # Reset the last printed line index

            if not no_lyrics:
                progress_ms = current_song.progress
                start_time = time.time()
                while time.time() - start_time <= 5:  # Adjust the timer duration as needed
                    for i, line in enumerate(lyrics):
                        difference = (time.time() - start_time) * 1000
                        if int(progress_ms + difference - 50 <= int(line['startTimeMs']) <= int(progress_ms + difference + 50)):
                            if i != last_line_index:  # Check if it's a new line
                                print(Fore.RESET + "\rLyrics: " + line['words'] + spaces, end='')
                                client.send_message("/chatbox/input", [line['words'], True, False])  # Send message
                                last_line_index = i
        else:
            time.sleep(2)

    except TypeError:
        print(Fore.RED + "Unable to fetch lyrics")
        no_lyrics = True
