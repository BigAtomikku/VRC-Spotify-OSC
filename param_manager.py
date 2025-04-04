from pythonosc.udp_client import SimpleUDPClient
import time


class ParamManager:
    OSC_LYRICS_PATH = "/Atomikku/VRCSpotifyOSC/Lyrics"

    def __init__(self, ip, port, song_data_queue, running, gui):
        self.client = SimpleUDPClient(ip, port)
        self.song_data_queue = song_data_queue
        self.running = running
        self.gui = gui
        self.track = None
        self.last_lyric = None

    def send_osc_message(self, message):
        self.client.send_message(self.OSC_LYRICS_PATH, message)

    def handle_song_update(self):
        self.gui.update_labels(self.track['name'], self.track['artists'][0]['name'], "")
        self.send_osc_message("")

    def handle_play_pause(self, is_playing):
        self.send_osc_message(self.last_lyric) if is_playing else self.send_osc_message("")

    def handle_lyric_update(self, lyric):
        self.gui.update_lyric(lyric)
        self.send_osc_message(lyric)
        self.last_lyric = lyric

    def process_queue_messages(self):
        while not self.song_data_queue.empty():
            message = self.song_data_queue.get_nowait()
            message_type = message['type']
            print(f"Got message: {message}")

            if message_type == 'song_update':
                self.track = message['playback']['item']
                self.handle_song_update()

            elif message_type == 'is_playing':
                self.handle_play_pause(message['is_playing'])

            elif message['type'] == 'lyric_update':
                if message['lyric'] is None:
                    self.gui.update_lyric("Lyrics for this track are not available")
                self.handle_lyric_update(message['lyric'])

    def run(self):
        while self.running.is_set():
            self.process_queue_messages()
            time.sleep(0.1)

        self.send_osc_message("")
