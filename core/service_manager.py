import queue
import config
import asyncio
import threading
from core import lrc, ChatboxManager, ParamManager


class ServiceManager:
    def __init__(self):
        self.running = threading.Event()
        self.lrc_thread = None
        self.osc_thread = None
        self.queue = queue.Queue()
        self.lock = threading.Lock()

    def start(self, handlers):
        with self.lock:
            if self.running.is_set():
                return

            print("[ServiceManager] Starting Services...")
            self.running.set()
            ip = config.get('ip')
            port = config.get('port')

            self.lrc_thread = threading.Thread(target=lambda: self._run_lrc(handlers), daemon=True)
            osc = self._create_osc_manager(ip, port)
            self.osc_thread = threading.Thread(target=osc.run, daemon=True)

            self.lrc_thread.start()
            self.osc_thread.start()

    def stop(self):
        with self.lock:
            if not self.running.is_set():
                return

            print("[ServiceManager] Stopping Services...")
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

    def _run_lrc(self, handlers):
        try:
            asyncio.run(lrc(self.queue, self.running, handlers))
        except Exception as e:
            print(f"[ServiceManager] Fatal error in LRC: {e}")
            if "Invalid client_id" in str(e):
                handlers.error("Invalid Spotify Client ID. Please check your configuration.")
            else:
                handlers.error("Program error occurred. Please check your config or restart.")
            self.running.clear()

    def _create_osc_manager(self, ip, port):
        if port == 9000:
            print("[ServiceManager] Using ChatboxManager")
            return ChatboxManager(ip, port, self.queue, self.running)
        else:
            print("[ServiceManager] Using ParamManager")
            return ParamManager(ip, port, self.queue, self.running)
