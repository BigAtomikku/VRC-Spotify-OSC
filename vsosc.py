import gui
import threading
import queue
from spotify_handler import spotify_thread
from osc_handler import osc_thread

running = threading.Event()
spotify_thread_handle = None
osc_thread_handle = None
song_data_queue = queue.Queue()


def is_running():
    return running.is_set()


def toggle_main(sp_dc, ip, port):
    global spotify_thread_handle, osc_thread_handle
    if not running.is_set():
        running.set()
        spotify_thread_handle = threading.Thread(target=spotify_thread, args=(sp_dc, song_data_queue, running), daemon=True)
        osc_thread_handle = threading.Thread(target=osc_thread, args=(ip, port, song_data_queue, running), daemon=True)
        spotify_thread_handle.start()
        osc_thread_handle.start()

    else:
        running.clear()
        spotify_thread_handle = None
        osc_thread_handle = None

        # Clear the queue
        while not song_data_queue.empty():
            try:
                song_data_queue.get_nowait()
            except queue.Empty:
                break

if __name__ == "__main__":
    gui.start_gui()