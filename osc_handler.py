from pythonosc.udp_client import SimpleUDPClient
import gui
import time

def connect_to_osc(ip, port):
    client = SimpleUDPClient(ip, port)
    return client


# Gets current lyric in song
def current_lyric(user_time, lyrics):
    key = max((k for k in lyrics.keys() if k < user_time), default=None)
    return lyrics.get(key)

# OSC Thread: handles GUI and OSC updates
def osc_thread(ip, port, song_data_queue, running):
    client = connect_to_osc(ip, port)
    current_song_info = None
    current_song = ""
    lyrics = {}
    previous_lyric = ""
    last_update_time = time.time()
    paused_displayed = False
    refresh_timeout = 5

    while running.is_set():
        # Process messages from the Spotify thread
        while not song_data_queue.empty():
            message = song_data_queue.get_nowait()

            if message['type'] == 'update':
                current_song_info = message['song_info']

            elif message['type'] == 'new_lyrics':
                previous_lyric = ""
                lyrics = message['lyrics']

            elif message['type'] == 'no_lyrics':
                lyrics = {}
                gui.update_lyric("Lyrics for this track are not available on Spotify")

        # If we don't have song info yet, wait
        if current_song_info is None:
            time.sleep(0.1)
            continue

        song_display = f"{current_song_info['name']} - {current_song_info['artist']}"
        current_time = time.time()
        time_since_last_update = current_time - last_update_time
        needs_refresh = time_since_last_update >= refresh_timeout

        # Handle song change
        if current_song != current_song_info['uri']:
            current_song = current_song_info['uri']
            lyrics = {}
            gui.update_song(song_display)
            gui.clear_lyric()
            last_update_time = current_time

        # Handle paused state
        if not current_song_info['is_playing']:
            if not paused_displayed or needs_refresh:
                paused_displayed = True
                song_paused_message = f"\U000023F8 {song_display}"
                gui.update_lyric("Paused")
                client.send_message("/chatbox/input", [song_paused_message, True, False])
                client.send_message("/Atomikku/VRCSpotifyOSC/Lyrics", "")
                last_update_time = current_time
                continue
        else:
            paused_displayed = False

        if lyrics:
            # We have lyrics - find current lyric
            user_time = current_song_info['progress_ms']
            lyric = current_lyric(user_time, lyrics)
            lyric_changed = lyric != previous_lyric

            if lyric_changed or needs_refresh:
                if lyric_changed:
                    previous_lyric = lyric

                if lyric == "♪":
                    lyric = None

                if lyric:
                    gui.update_lyric(lyric)
                    lyric_message = f"\U000025B6 {song_display} \n \U0001F3A4 {lyric}"
                    client.send_message("/chatbox/input", [lyric_message, True, False])
                    client.send_message("/Atomikku/VRCSpotifyOSC/Lyrics", f"\U0001F3A4 {lyric}")
                else:
                    gui.clear_lyric()
                    song_play_message = f"\U000025B6 {song_display}"
                    client.send_message("/chatbox/input", [song_play_message, True, False])
                    client.send_message("/Atomikku/VRCSpotifyOSC/Lyrics", "")

                last_update_time = current_time

        elif needs_refresh:
            # No lyrics - just refresh song info periodically
            gui.update_lyric("Lyrics for this track are not available on Spotify")
            song_play_message = f"\U000025B6 {song_display}"
            client.send_message("/chatbox/input", [song_play_message, True, False])
            last_update_time = current_time

        # Small sleep to prevent CPU hogging
        time.sleep(0.1)

    # Handle shutdown
    client.send_message("/Atomikku/VRCSpotifyOSC/Lyrics", "")