import threading
import queue

from lrc_worker import lrc_thread
from chatbox_manager import ChatboxManager
from param_manager import ParamManager

running = threading.Event()
lrc_thread_handle = None
osc_thread_handle = None
song_data_queue = queue.Queue()


def is_running():
    return running.is_set()


def toggle_main(client_id, ip, port, gui_instance):
    global lrc_thread_handle, osc_thread_handle
    if not running.is_set():
        running.set()
        lrc_thread_handle = threading.Thread(target=lrc_thread, args=(client_id, song_data_queue, running), daemon=True)

        if port == 9000:
            osc_client = ChatboxManager(ip, port, song_data_queue, running, gui_instance)
            osc_thread_handle = threading.Thread(target=osc_client.run, daemon=True)

        else:
            param_manager = ParamManager(ip, port, song_data_queue, running, gui_instance)
            osc_thread_handle = threading.Thread(target=param_manager.run, daemon=True)

        lrc_thread_handle.start()
        osc_thread_handle.start()

    else:
        running.clear()
        lrc_thread_handle = None
        osc_thread_handle = None

        # Clear the queue
        while not song_data_queue.empty():
            try:
                song_data_queue.get_nowait()
            except queue.Empty:
                break
