import time
from syrics.api import Spotify
from pythonosc.udp_client import SimpleUDPClient

sp = Spotify('COOKIE')
ip = "127.0.0.1"
port = 9000

client = SimpleUDPClient(ip, port)  # Create client

print("Connected to Client")

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

while True:
    current_song_data = sp.get_current_song()
    current_song = CurrentSong(current_song_data)

    try:

        if current_song.playing:
            if current_song.name + current_song.artist != song:
                print("Now playing: " + current_song.name + " by " + current_song.artist)
                client.send_message("/chatbox/input", ["Now playing: " + current_song.name + " by " + current_song.artist, True, False])  # Send message
                lyrics = sp.get_lyrics(current_song.uri)['lyrics']['lines']
                song = current_song.name + current_song.artist
                last_line_index = -1  # Reset the last printed line index

            progress_ms = current_song.progress

            start_time = time.time()
            while time.time() - start_time <= 5:  # Adjust the timer duration as needed
                for i, line in enumerate(lyrics):
                    difference = (time.time() - start_time) * 1000
                    if int(progress_ms + difference - 30 <= int(line['startTimeMs']) <= int(progress_ms + difference + 30)):
                        if i != last_line_index:  # Check if it's a new line
                            print(line['words'])
                            client.send_message("/chatbox/input", [line['words'], True, False])  # Send message
                            last_line_index = i
        else:
            time.sleep(2)

    except TypeError:
        print("Unable to fetch lyrics")
