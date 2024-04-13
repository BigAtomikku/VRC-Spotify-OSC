import sys
import time
import json
import ctypes
import syrics.exceptions
from colorama import Fore
import requests.exceptions
from syrics.api import Spotify
from pythonosc.udp_client import SimpleUDPClient


# Disables quick edit mode to avoid console pauses """
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


# Returns spotify instance using sp_dc token given in the config.json file
"""def get_spotify_instance():
    try:
        with open('config.json', 'r') as file:
            data = json.load(file)
            sp_dc = data.get('sp_dc', None)
    except FileNotFoundError:
        print(Fore.RED + "Error: config.json file not found.")
        time.sleep(5)
        sys.exit()

    if not sp_dc:
        print(Fore.RED + "sp_dc key is not present or has no value in the config.json file.")
        time.sleep(5)
        sys.exit()

    try:
        return Spotify(sp_dc)
    except syrics.exceptions.NotValidSp_Dc:
        print(Fore.RED + "sp_dc provided is invalid, please check it and update the .env file")
        time.sleep(5)
        sys.exit() """

def load_config(filename, keys):
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
            values = [data.get(key) for key in keys]
            if None in values:
                print(Fore.RED + "One or more keys are missing in the config file:", keys)
                time.sleep(5)
                sys.exit()
            return values
    except FileNotFoundError:
        print(Fore.RED + f"Error: {filename} file not found.")
        time.sleep(5)
        sys.exit()


# Returns array of data for current song
def current_data(sp):
    data = sp.get_current_song()
    try:
        uri = data['item']['id']
    except TypeError:
        return
    name = data['item']['name']
    artist = data['item']['artists'][0]['name']
    progress = data['progress_ms']
    playing = data['is_playing']
    return [uri, name, artist, progress, playing]


# Returns dictionary of times associated with lyrics
def lyrics_dictionary(data):
    lyrics_data = data['lyrics']['lines']
    lyrics_dic = {int(line['startTimeMs']): line['words'] for line in lyrics_data}
    return lyrics_dic


# Gets current lyric in song
def current_lyric(user_time, lyrics):
    key = max((k for k in lyrics.keys() if k < user_time), default=None)
    return lyrics.get(key)


# Clears the current line in the console
def clear_console_line():
    UP = '\033[1A'
    CLEAR = '\x1b[2K'
    print(UP, end=CLEAR)


# Main method
def main():
    if not disable_quick_edit_mode():
        print(Fore.RED + "Failed to disable Quick Edit mode")

    #sp = get_spotify_instance()
    #ip, port = "127.0.0.1", 9000

    sp_dc = load_config('config.json', ['sp_dc'])[0]
    print(sp_dc)
    sp = Spotify(sp_dc)
    ip, port = load_config('config.json', ['ip', 'port'])


    client = SimpleUDPClient(ip, port)  # Create client
    print(Fore.RESET + "Connected to Client\n",)

    song = ''
    lyrics = {}
    no_lyrics = False
    last_line_index = ''

    while True:
        try:
            current_song = current_data(sp)
        except syrics.exceptions.NoSongPlaying:
            print(Fore.YELLOW + "No song detected, trying again.")
            continue

        try:
            if current_song[1] + current_song[2] != song:
                clear_console_line()
                print(Fore.MAGENTA + "Now playing: " + current_song[1] + " by " + current_song[2])
                client.send_message("/chatbox/input", ["Now playing: " + current_song[1] + " by " +
                                                       current_song[2], True, False])  # Send message
                client.send_message("/Atomikku/VRCSpotifyOSC/Lyrics", "") #send blank on new song, just incase new song doesn't have lyrics (so previous lyrics don't stay frozen)
                song = current_song[1] + current_song[2]
                time.sleep(3)
                lyrics_data = sp.get_lyrics(current_song[0])

                if lyrics_data:
                    no_lyrics = False
                    last_line_index = ''
                    lyrics = lyrics_dictionary(lyrics_data)

                else:
                    no_lyrics = True
                    print(Fore.YELLOW + "Lyrics for this track are not available on spotify")

            if current_song[4]:
                if not no_lyrics:
                    user_time = current_song[3]
                    lyric = current_lyric(user_time, lyrics)
                    if last_line_index != lyric:
                        if last_line_index != '':
                            clear_console_line()
                        print(Fore.RESET + "Lyrics: " + lyric)
                        client.send_message("/chatbox/input", [lyric, True, False])
                        client.send_message("/Atomikku/VRCSpotifyOSC/Lyrics", lyric)
                        last_line_index = lyric

            else:
                clear_console_line()
                print(Fore.RESET + "Paused")
                time.sleep(1)

        except (requests.exceptions.ConnectionError, TypeError):
            continue


main()
