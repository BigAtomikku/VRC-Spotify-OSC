from pythonosc.udp_client import SimpleUDPClient
from syrics.api import Spotify
import requests.exceptions
import syrics.exceptions
import threading
import json
import time
import sys
import gui

running = False

def is_running():
    return running

def start_main():
    if not running:
        threading.Thread(target=main, daemon=True).start()

def stop_main():
    global running
    running = False

def load_config(filename, keys):
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
            values = [data.get(key) for key in keys]

            if None in values:
                print("One or more keys are missing in the config file:", keys)
                time.sleep(5)
                sys.exit()

            return values
    except FileNotFoundError:
        print("Config file missing")
        gui.update_lyric("Config file missing, open settings to create one")
        gui.force_stop_program()


# Returns spotify instance using sp_dc token given in the config.json file
def get_spotify_instance(sp_dc):
    if not sp_dc:
        print("sp_dc key is not present or has no value in the config.json file.")
        gui.update_lyric("sp_dc key invalid, please check it and update settings")
        gui.force_stop_program()

    try:
        return Spotify(sp_dc)
    except syrics.exceptions.NotValidSp_Dc:
        print("sp_dc key is invalid, please check it and update the config.json file.")
        gui.update_lyric("sp_dc key invalid, please check it and update settings")
        gui.force_stop_program()


# Connect to spotify (via syrics) using config
def connect_to_spotify():
    try:
        sp_dc, ip, port = load_config('config.json', ['sp_dc', 'ip', 'port'])
        client = SimpleUDPClient(ip, port)
        sp = get_spotify_instance(sp_dc)
        print("Connected to Client\n")
        return sp, client
    except TypeError:
        gui.update_lyric("Config file missing, open settings to create one")
        gui.start_stop_button.config(text="Start")
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

    sp, client = connect_to_spotify()
    song = ''
    lyrics = {}
    previous_lyric = ''
    stale_update_count = 0
    paused_displayed = False

    while running:
        try:
            current_song = current_data(sp)
            song_play_message = f"\U000025B6 {current_song['name']} - {current_song['artist']}"
            song_paused_message = f"\U000023F8 {current_song['name']} - {current_song['artist']}"
            paused = not current_song['is_playing']
        except syrics.exceptions.NoSongPlaying:
            print("Access token expired, reconnecting")
            sp, _ = connect_to_spotify()
            print("Connected to Client\n")
            continue

        if current_song['name'] + " by " + current_song['artist'] != song:
            song = current_song['name'] + " by " + current_song['artist']
            print("Now playing: " + song)
            gui.update_song(current_song['name'], current_song['artist'])
            gui.update_lyric("")
            client.send_message("/chatbox/input", [song_play_message, True, False])
            client.send_message("/Atomikku/VRCSpotifyOSC/Lyrics", "") # send blank on new song, just incase new song doesn't have lyrics (so previous lyrics don't stay frozen)
            lyrics_data = sp.get_lyrics(current_song['uri'])

            if lyrics_data:
                previous_lyric = ''
                lyrics = lyrics_dictionary(lyrics_data)
            else:
                lyrics = {}
                print("Lyrics for this track are not available on spotify")
                gui.update_lyric("Lyrics for this track are not available on spotify")

        if paused:
            if not paused_displayed:
                gui.update_lyric("Paused")
                client.send_message("/chatbox/input",[song_paused_message, True, False])
                print("Paused")
                paused_displayed = True
                stale_update_count = 0
            else:
                if stale_update_count == 80:
                    client.send_message("/chatbox/input",[song_paused_message, True, False])
                    stale_update_count = 0
                else:
                    stale_update_count += 1

        if not paused:
            if lyrics:
                user_time = current_song['progress_ms']
                lyric = current_lyric(user_time, lyrics)
                lyric_message = f"\U000025B6 {current_song['name']} - {current_song['artist']} \n \U0001F3A4 {lyric}"

                if previous_lyric != lyric or paused_displayed:
                    stale_update_count = 0
                    previous_lyric = lyric
                    paused_displayed = False

                    if lyric:
                        print("Lyrics: " + lyric)
                        gui.update_lyric(lyric)
                        client.send_message("/chatbox/input", [lyric_message, True, False])
                        client.send_message("/Atomikku/VRCSpotifyOSC/Lyrics", lyric)
                    else:
                        client.send_message("/chatbox/input", [song_play_message, True, False])
                        client.send_message("/Atomikku/VRCSpotifyOSC/Lyrics", lyric)

                else:
                    if stale_update_count == 80:
                        print("Sending same lyric")
                        stale_update_count = 0
                        if lyric:
                            client.send_message("/chatbox/input", [lyric_message, True, False])
                            client.send_message("/Atomikku/VRCSpotifyOSC/Lyrics", lyric)
                        else:
                            client.send_message("/chatbox/input", [song_play_message, True, False])
                    else:
                        stale_update_count += 1

            if not lyrics:
                if paused_displayed:
                    gui.update_lyric("Lyrics for this track are not available on spotify")
                    client.send_message("/chatbox/input", [song_play_message, True, False])
                    paused_displayed = False

                if stale_update_count == 80:
                    client.send_message("/chatbox/input", [song_play_message, True, False])
                    stale_update_count = 0
                else:
                    stale_update_count += 1
