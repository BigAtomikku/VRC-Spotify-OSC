from pythonosc.udp_client import SimpleUDPClient
import time


class BaseOSCManager:
    def __init__(self, ip, port, song_data_queue, running, osc_path):
        self.client = SimpleUDPClient(ip, port)
        self.song_data_queue = song_data_queue
        self.running = running
        self.track = None
        self.last_lyric = ""
        self.osc_path = osc_path
        self.is_playing = None

    def send_osc_message(self, lyric=None):
        if lyric is not None:
            self.client.send_message(self.osc_path, [lyric, True, False])

        else:
            self.client.send_message(self.osc_path, self.last_lyric) if self.is_playing \
                else self.client.send_message(self.osc_path, ["", True, False])

    def handle_song_update(self, playback):
        self.last_lyric = None
        self.track = playback
        self.send_osc_message()

    def handle_lyric_update(self, lyric):
        raise NotImplementedError("Subclasses should implement this method")

    def process_queue_messages(self):
        while not self.song_data_queue.empty():
            message = self.song_data_queue.get_nowait()
            message_type = message['type']
            print(f"Got message: {message}")

            if message_type == 'song_update':
                self.handle_song_update(message['playback'])

            elif message_type == 'is_playing':
                self.is_playing = message['is_playing']
                self.send_osc_message()

            elif message['type'] == 'lyric_update':
                self.handle_lyric_update(message['lyric'])

    def update(self):
        raise NotImplementedError("Subclasses should implement this method")

    def run(self):
        while self.running.is_set():
            self.process_queue_messages()
            self.update()
            time.sleep(0.1)

        self.client.send_message(self.osc_path, ["", True, False])
        print(f"[{self.__class__.__name__}] Exiting cleanly")


class ChatboxManager(BaseOSCManager):
    OSC_CHATBOX_PATH = "/chatbox/input"
    PLAY_EMOJI = "\U000025B6"
    PAUSE_EMOJI = "\U000023F8"
    MIC_EMOJI = "\U0001F3A4"

    def __init__(self, ip, port, song_data_queue, running):
        super().__init__(ip, port, song_data_queue, running, self.OSC_CHATBOX_PATH)
        self.last_update_time = time.time()
        self.refresh_timeout = 10
        self.is_playing = None

    def send_osc_message(self, lyric=None):
        emoji = self.PLAY_EMOJI if self.is_playing else self.PAUSE_EMOJI
        song_display = f"{emoji} {self.track.name} - {self.track.artists[0]['name']}"

        if self.is_playing:
            if lyric is not None:
                if lyric != "" and lyric != "♪":
                    song_display += f" \n {self.MIC_EMOJI} {lyric}"
            elif self.last_lyric:
                song_display += f" \n {self.MIC_EMOJI} {self.last_lyric}"

        self.client.send_message(self.osc_path, [song_display, True, False])
        self.last_update_time = time.time()

    def handle_lyric_update(self, lyric):
        self.send_osc_message(lyric=lyric)
        self.last_lyric = lyric

    def update(self):
        if not self.track:
            return

        if time.time() - self.last_update_time >= self.refresh_timeout:
            self.send_osc_message()


class ParamManager(BaseOSCManager):
    OSC_LYRICS_PATH = "/Atomikku/VRCSpotifyOSC/Lyrics"

    def __init__(self, ip, port, song_data_queue, running):
        super().__init__(ip, port, song_data_queue, running, self.OSC_LYRICS_PATH)

    def handle_lyric_update(self, lyric):
        if lyric == "♪":
            self.send_osc_message("")
        else:
            self.send_osc_message(lyric)
        self.last_lyric = lyric

    def update(self):
        pass
