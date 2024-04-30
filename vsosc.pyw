from pythonosc.udp_client import SimpleUDPClient
from gui import start_gui, update_lyric, update_song
# from listener import start_server
from syrics.api import Spotify
import requests.exceptions
from colorama import Fore
import syrics.exceptions
import threading
import json
import time
import sys

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
        print(Fore.YELLOW + "Config file missing. Creating new config")
        sp_dc = input(Fore.RESET + "Enter sp_dc token: ")
        ip = input("Enter server IP address (e.g., 127.0.0.1): ")
        port = input("Enter server port (e.g., 9000): ")
        data = {"sp_dc": sp_dc, "ip": ip, "port": int(port)}

        with open("config.json", 'w') as json_file:
            json.dump(data, json_file)
        values = [data.get(key) for key in keys]

        if None in values:
            print(Fore.RED + "One or more keys are missing in the config file:", keys)
            time.sleep(5)
            sys.exit()

        return values


# Returns spotify instance using sp_dc token given in the config.json file
def get_spotify_instance(sp_dc):
    if not sp_dc:
        print(Fore.RED + "sp_dc key is not present or has no value in the config.json file.")
        time.sleep(5)
        sys.exit()

    try:
        return Spotify(sp_dc)
    except syrics.exceptions.NotValidSp_Dc:
        print(Fore.RED + "sp_dc provided is invalid, please check it and update the config.json file.")
        time.sleep(5)
        sys.exit()


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
    sp_dc, ip, port = load_config('config.json', ['sp_dc', 'ip', 'port'])
    sp = get_spotify_instance(sp_dc)
    client = SimpleUDPClient(ip, port)
    print(Fore.LIGHTGREEN_EX + "Connected to Client\n")

    song = ''
    lyrics = {}
    paused = False
    no_lyrics = False
    last_line_index = ''
    # threading.Thread(target=start_server, daemon = True).start() # Activate listener (NOT DONE IMPLEMENTING)
    threading.Thread(target=start_gui, daemon = True).start()

    while True:
        try:
            current_song = current_data(sp)
        except syrics.exceptions.NoSongPlaying:
            time.sleep(1)
            input(Fore.YELLOW + "No song detected, press enter to try again")
            sp = get_spotify_instance(sp_dc)
            print(Fore.RESET + "Connected to Client\n")
            continue

        try:
            if current_song['name'] + current_song['artist'] != song:
                if last_line_index != '' or paused:
                    paused = False

                print(Fore.MAGENTA + "Now playing: " + current_song['name'] + " by " + current_song['artist'])
                update_song(current_song['name'], current_song['artist'])
                update_lyric("")
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

            if current_song['is_playing']:
                if not no_lyrics:
                    user_time = current_song['progress_ms']
                    lyric = current_lyric(user_time, lyrics)
                    if last_line_index != lyric:
                        paused = False
                        print(Fore.RESET + "Lyrics: " + lyric)
                        update_lyric(lyric)
                        client.send_message("/chatbox/input", [f"\U000025B6 {current_song['name']} - {current_song['artist']} \n {lyric}", True, False])
                        client.send_message("/Atomikku/VRCSpotifyOSC/Lyrics", lyric)
                        last_line_index = lyric

            else:
                if not paused:
                    paused = True
                    update_lyric("Paused")
                    client.send_message("/chatbox/input", [f"\U000023F8 {current_song['name']} - {current_song['artist']}", True, False])
                    if not no_lyrics:
                        print(Fore.RESET + "Paused")
                    time.sleep(1)

        except (requests.exceptions.ConnectionError, TypeError):
            continue

main()
