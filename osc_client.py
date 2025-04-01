from pythonosc.udp_client import SimpleUDPClient
import time


class OSCClient:
    OSC_CHATBOX_PATH = "/chatbox/input"
    OSC_LYRICS_PATH = "/Atomikku/VRCSpotifyOSC/Lyrics"

    PLAY_EMOJI = "\U000025B6"
    PAUSE_EMOJI = "\U000023F8"
    MIC_EMOJI = "\U0001F3A4"

    def __init__(self, ip, port, song_data_queue, running, gui):
        self.client = SimpleUDPClient(ip, port)
        self.song_data_queue = song_data_queue
        self.running = running
        self.gui = gui
        self.track = None
        self.last_sent = ""
        self.last_update_time = time.time()
        self.refresh_timeout = 5

    def handle_song_update(self):
        self.gui.update_labels(self.track['name'], self.track['artists'][0]['name'], "Searching for Lyrics")
        self.client.send_message(self.OSC_LYRICS_PATH, "")

    def handle_play_pause(self, is_playing):
        emoji = self.PLAY_EMOJI if is_playing else self.PAUSE_EMOJI
        song_display = f"{emoji} {self.track['name']} - {self.track['artists'][0]['name']}"
        self.client.send_message(self.OSC_CHATBOX_PATH, [song_display, True, False])
        self.gui.update_lyric("" if is_playing else "Paused")
        self.last_sent = song_display

    def handle_lyric_update(self, lyric):
        song_display = f"{self.PLAY_EMOJI} {self.track['name']} - {self.track['artists'][0]['name']}"

        if lyric != "":
            song_display += f" \n {self.MIC_EMOJI} {lyric}"

        self.gui.update_lyric(lyric)
        self.client.send_message(self.OSC_LYRICS_PATH, lyric)
        self.client.send_message(self.OSC_CHATBOX_PATH, [song_display, True, False])
        self.last_sent = song_display

    def process_queue_messages(self):
        while not self.song_data_queue.empty():
            message = self.song_data_queue.get_nowait()
            message_type = message['type']

            print(f"Got message: {message}")

            if message_type == 'song_update':
                self.track = message['playback']
                self.handle_song_update()

            elif message_type == 'is_playing':
                self.handle_play_pause(message['is_playing'])

            elif message['type'] == 'lyric_update':
                if message['lyric'] is None:
                    self.gui.handle_lyric_update("Lyrics for this track are not available")
                self.handle_lyric_update(message['lyric'])

            self.last_update_time = time.time()

    def update(self):
        if not self.track or self.track.get('message') == 'No track currently playing':
            return

        if time.time() - self.last_update_time >= self.refresh_timeout:
            self.client.send_message(self.OSC_CHATBOX_PATH, [self.last_sent, True, False])
            self.last_update_time = time.time()

    def run(self):
        while self.running.is_set():
            self.process_queue_messages()
            self.update()
            time.sleep(0.1)

        # Handle shutdown
        self.client.send_message(self.OSC_CHATBOX_PATH, ["Shutting Down", True, False])
        self.client.send_message(self.OSC_LYRICS_PATH, "")
