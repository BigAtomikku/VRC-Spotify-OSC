import queue
import asyncio
import threading
from core import lrc_loop, ChatboxManager, ParamManager


class ServiceManager:
    def __init__(self):
        self.running = threading.Event()
        self.lrc_thread = None
        self.osc_thread = None
        self.queue = queue.Queue()
        self.lock = threading.Lock()

    def start(self, provider, key, ip, port, handlers):
        with self.lock:
            if not self.running.is_set():
                self.running.set()

                def run_lrc_loop():
                    print("[ServiceManager] Starting LRC loop...")
                    asyncio.run(lrc_loop(provider, key, self.queue, self.running, handlers))

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
        with self.lock:
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
