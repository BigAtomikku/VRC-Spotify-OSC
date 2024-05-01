from pythonosc.udp_client import SimpleUDPClient
# from listener import start_server
from syrics.api import Spotify
import requests.exceptions
from colorama import Fore
import syrics.exceptions
import threading
import json
import time
import sys
import gui

running = False

def is_running():
    global running
    return running

def start_main():
    global running
    if not running:
        threading.Thread(target=main).start()

def stop_main():
    global running
    running = False

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
        print(Fore.YELLOW + "Config file missing")
        gui.update_lyric("Config file missing, open settings to create one")
        gui.force_stop_program()

# Returns spotify instance using sp_dc token given in the config.json file
def get_spotify_instance(sp_dc):
    if not sp_dc:
        print(Fore.RED + "sp_dc key is not present or has no value in the config.json file.")
        gui.update_lyric("sp_dc key invalid, please check it and update settings")
        gui.force_stop_program()

    try:
        return Spotify(sp_dc)
    except syrics.exceptions.NotValidSp_Dc:
        print(Fore.RED + "sp_dc key is invalid, please check it and update the config.json file.")
        gui.update_lyric("sp_dc key invalid, please check it and update settings")
        gui.force_stop_program()


# Returns array of data for current song
def current_data(sp):
    data = sp.get_current_song()

    try:
        song_info = {
            'uri' : data['item']['id'],
            'name' : data['item']['name'],
            'artist' : data['item']['artists'][0]['name'],
            'progress_ms' : data['progress_ms'],
            'is_playing' : data['is_playing']
        }

    except TypeError:
        return

    return song_info


# Returns dictionary of times associated with lyrics
def lyrics_dictionary(data):
    lyrics_data = data['lyrics']['lines']
    lyrics_dic = {int(line['startTimeMs']): line['words'] for line in lyrics_data}
    return lyrics_dic


# Gets current lyric in song
def current_lyric(user_time, lyrics):
    key = max((k for k in lyrics.keys() if k < user_time), default=None)
    return lyrics.get(key)

# Main method
def main():
    global running
    running = True

    try:
        sp_dc, ip, port = load_config('config.json', ['sp_dc', 'ip', 'port'])
        sp = get_spotify_instance(sp_dc)
        client = SimpleUDPClient(ip, port)
        print(Fore.LIGHTGREEN_EX + "Connected to Client\n")

    except TypeError:
        gui.update_lyric("config file missing, open settings to create one")
        gui.start_stop_button.config(text="Start")
        gui.force_stop_program()

    song = ''
    lyrics = {}
    paused = False
    no_lyrics = False
    last_line_index = ''
    # threading.Thread(target=start_server, daemon = True).start() # Activate listener (NOT DONE IMPLEMENTING)

    while running:
        try:
            current_song = current_data(sp)
        except syrics.exceptions.NoSongPlaying:
            time.sleep(1)
            print("Access token expired, reconnecting")
            sp = get_spotify_instance(sp_dc)
            print(Fore.RESET + "Connected to Client\n")
            continue

        try:
            if current_song['name'] + current_song['artist'] != song:
                if last_line_index != '' or paused:
                    paused = False

                print(Fore.MAGENTA + "Now playing: " + current_song['name'] + " by " + current_song['artist'])
                gui.update_song(current_song['name'], current_song['artist'])
                gui.update_lyric("")
                client.send_message("/chatbox/input", [f"\U000025B6 {current_song['name']} - {current_song['artist']}", True, False])
                client.send_message("/Atomikku/VRCSpotifyOSC/Lyrics", "") # send blank on new song, just incase new song doesn't have lyrics (so previous lyrics don't stay frozen)
                song = current_song['name'] + current_song['artist']
                lyrics_data = sp.get_lyrics(current_song['uri'])

                if lyrics_data:
                    no_lyrics = False
                    last_line_index = ''
                    lyrics = lyrics_dictionary(lyrics_data)

                else:
                    no_lyrics = True
                    print(Fore.YELLOW + "Lyrics for this track are not available on spotify")
                    gui.update_lyric("Lyrics for this track are not available on spotify")

            if current_song['is_playing']:
                if not no_lyrics:
                    user_time = current_song['progress_ms']
                    lyric = current_lyric(user_time, lyrics)
                    if last_line_index != lyric:
                        paused = False
                        print(Fore.RESET + "Lyrics: " + lyric)
                        gui.update_lyric(lyric)
                        client.send_message("/chatbox/input", [f"\U000025B6 {current_song['name']} - {current_song['artist']} \n {lyric}", True, False])
                        client.send_message("/Atomikku/VRCSpotifyOSC/Lyrics", lyric)
                        last_line_index = lyric

            else:
                if not paused:
                    paused = True
                    gui.update_lyric("Paused")
                    client.send_message("/chatbox/input", [f"\U000023F8 {current_song['name']} - {current_song['artist']}", True, False])
                    if not no_lyrics:
                        print(Fore.RESET + "Paused")
                    time.sleep(1)

        except (requests.exceptions.ConnectionError, TypeError):
            continue
