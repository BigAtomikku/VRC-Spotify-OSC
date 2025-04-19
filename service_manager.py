import threading
import asyncio
import queue

from lrc_worker import lrc_loop
from chatbox_manager import ChatboxManager
from param_manager import ParamManager


class ServiceManager:
    def __init__(self):
        self.running = threading.Event()
        self.lrc_thread = None
        self.osc_thread = None
        self.queue = queue.Queue()

    def start(self, client_id, ip, port, update_cb):
        if not self.running.is_set():
            self.running.set()

            def run_lrc_loop():
                print("[ServiceManager] Starting LRC loop...")
                asyncio.run(lrc_loop(client_id, self.queue, self.running, update_cb))

            self.lrc_thread = threading.Thread(target=run_lrc_loop, daemon=True)

            if port == 9000:
                print("[ServiceManager] Starting Chatbox Manager...")
                osc = ChatboxManager(ip, port, self.queue, self.running)
            else:
                print("[ServiceManager] Starting Param Manager...")
                osc = ParamManager(ip, port, self.queue, self.running)

            self.osc_thread = threading.Thread(target=osc.run, daemon=True)
            self.lrc_thread.start()
            self.osc_thread.start()

    def stop(self):
        self.running.clear()

        if self.lrc_thread and self.lrc_thread.is_alive():
            self.lrc_thread.join()
        if self.osc_thread and self.osc_thread.is_alive():
            self.osc_thread.join()

        self.lrc_thread = None
        self.osc_thread = None

        while not self.queue.empty():
            try:
                self.queue.get_nowait()
            except queue.Empty:
                break
