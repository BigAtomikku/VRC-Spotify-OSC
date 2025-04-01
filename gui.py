from tkinter import Label, Tk, Button, Toplevel, Entry, Frame
from vsosc import toggle_main, is_running
from config import ConfigManager


class GUI:
    def __init__(self):
        self.config = ConfigManager()
        self.settings_window_open = False
        self.window = Tk()
        self.title_label = None
        self.artist_label = None
        self.lyrics_label = None
        self.start_stop_button = None
        self.client_id_entry = None
        self.ip_entry = None
        self.port_entry = None

    def start_gui(self):
        self.window.title("VRC Spotify OSC v2.1.0")
        self.window.geometry("600x185")
        self.window.configure(bg="#222")
        self.window.resizable(False, False)

        self.title_label = Label(self.window, text="VRC Spotify OSC", font=("Segoe UI SemiBold", 16), bg="#222",
                                 fg="white")
        self.title_label.pack(padx=10, pady=(10, 0))

        self.artist_label = Label(self.window, text="Press start to activate", font=("Segoe UI", 14), bg="#222", fg="white")
        self.artist_label.pack(padx=10, pady=(0, 10))

        self.lyrics_label = Label(self.window, text="Remember to configure settings first!", font=("Segoe UI", 11), bg="#222", fg="white")
        self.lyrics_label.pack(padx=10, pady=(10, 0))

        settings_button = Button(self.window, text="Settings", font=("Segoe UI SemiBold", 9),
                                 command=self.open_settings, bg="#333", fg="white")
        settings_button.place(relx=0.03, rely=0.95, anchor='sw')

        self.start_stop_button = Button(self.window, text="Start" if not is_running() else "Stop",
                                        command=self.toggle_start_stop,
                                        font=("Segoe UI SemiBold", 10), bg="#333", fg="white", width=10)
        self.start_stop_button.pack(side='bottom', padx=20, pady=10)

        self.window.mainloop()

    def toggle_start_stop(self):
        client_id, ip, port = self.config.get("client_id"), self.config.get("ip"), self.config.get("port")

        if is_running():
            toggle_main(client_id, ip, port, self)
            self.start_stop_button.config(text="Start")
            self.update_labels("Program Stopped", "Press start to activate", "")
        else:
            toggle_main(client_id, ip, port, self)
            self.title_label.config(text="Program Started")
            self.artist_label.config(text="")
            self.lyrics_label.config(text="Play a song on spotify!")
            self.start_stop_button.config(text="Stop")

    def open_settings(self):
        if self.settings_window_open:
            return

        settings_window = Toplevel()
        settings_window.title("Settings")
        settings_window.geometry("346x150")
        settings_window.configure(bg="#222")

        settings_window.grab_set()
        self.settings_window_open = True
        settings_window.protocol("WM_DELETE_WINDOW", lambda: self.close_settings(settings_window))

        Label(settings_window, text="Client ID:", font=("Segoe UI SemiBold", 10), bg="#222", fg="white").grid(row=0,
                                                                                                              column=0,
                                                                                                              sticky='e',
                                                                                                              padx=(
                                                                                                              10, 2),
                                                                                                              pady=10)
        self.client_id_entry = Entry(settings_window, bg="#333", fg="white", insertbackground='white', width=41)
        self.client_id_entry.grid(row=0, column=1, padx=(2, 10), pady=10)
        self.client_id_entry.insert(0, self.config.get('client_id', 'Enter Client ID'))

        frame_ip_port = Frame(settings_window, bg="#222")
        frame_ip_port.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        Label(frame_ip_port, text="IP:", font=("Segoe UI SemiBold", 10), bg="#222", fg="white").pack(side="left",
                                                                                                     padx=5)
        self.ip_entry = Entry(frame_ip_port, bg="#333", fg="white", insertbackground='white', width=15)
        self.ip_entry.pack(side="left", padx=(5, 10))
        self.ip_entry.insert(0, self.config.get('ip', '127.0.0.1'))

        Label(frame_ip_port, text="Port:", font=("Segoe UI SemiBold", 10), bg="#222", fg="white").pack(side="left",
                                                                                                       padx=5)
        self.port_entry = Entry(frame_ip_port, bg="#333", fg="white", insertbackground='white', width=15)
        self.port_entry.pack(side="left", padx=(10, 5))
        self.port_entry.insert(0, self.config.get('port', '9000'))

        Button(settings_window, text="Update Config", command=lambda: self.update_config(settings_window), bg="#333",
               fg="white").grid(row=2, column=0, columnspan=2, padx=10, pady=20, sticky='nsew')

    def close_settings(self, settings_window):
        self.settings_window_open = False
        settings_window.destroy()

    def update_config(self, settings_window):
        self.config.update({
            "client_id": self.client_id_entry.get(),
            "ip": self.ip_entry.get(),
            "port": int(self.port_entry.get())
        })
        if is_running():
            self.toggle_start_stop()
        self.close_settings(settings_window)

    def update_title(self, text):
        self.title_label.configure(text=text)

    def update_artist(self, text):
        self.artist_label.configure(text=text)

    def update_lyric(self, text):
        self.lyrics_label.config(text=text)

    def get_lyric(self):
        return self.lyrics_label.get()

    def update_labels(self, title, artist, lyrics):
        self.update_title(title)
        self.update_artist(artist)
        self.update_lyric(lyrics)
