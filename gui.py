from tkinter import Label, Tk, Button, Frame, Entry, Toplevel
from vsosc import toggle_main, is_running
import json

global song_sync, lyrics, sp_dc_entry, ip_entry, port_entry, start_stop_button
global sp_dc, ip, port
settings_window_open = False

def start_gui():
    global start_stop_button
    window = Tk()
    window.title("VRC Spotify OSC v2.1.0")
    window.geometry("450x160")
    window.configure(bg="#222")
    window.resizable(False, False)

    global song_sync
    song_sync = Label(window, text="Program Stopped", font=("Segoe UI SemiBold", 15), bg="#222", fg="white")
    song_sync.pack(padx=10, pady=10)

    global lyrics
    lyrics = Label(window, text="", font=("Segoe UI", 11), bg="#222", fg="white")
    lyrics.pack(padx=10, pady=10)

    settings_button = Button(window, text="Settings", font=("Segoe UI SemiBold", 9), command=open_settings, bg="#333", fg="white")
    settings_button.place(relx=0.03, rely=0.95, anchor='sw')

    start_stop_button = Button(window, text="Start" if not is_running() else "Stop",
                               command=lambda: toggle_start_stop(),
                               font=("Segoe UI SemiBold", 10),
                               bg="#333",
                               fg="white",
                               width=10,)
    start_stop_button.pack(side='bottom', padx=20, pady=10)

    load_config()
    window.mainloop()

def toggle_start_stop():

    if is_running():
        toggle_main(sp_dc, ip, port)
        start_stop_button.config(text="Start")
        song_sync.config(text="Program Stopped")
        clear_lyric()
        return

    else:
        toggle_main(sp_dc, ip, port)
        song_sync.config(text="Program Started")
        lyrics.config(text="Play a song on spotify!")
        start_stop_button.config(text="Stop")

def open_settings():
    global settings_window_open
    if settings_window_open:
        return

    try:
        with open('config.json', 'r') as config_file:
            config_data = json.load(config_file)
    except (FileNotFoundError, json.JSONDecodeError):
        config_data = {}

    settings_window = Toplevel()
    settings_window.title("Settings")
    settings_window.geometry("346x150")
    settings_window.configure(bg="#222")

    settings_window.grab_set()
    settings_window_open = True

    settings_window.protocol("WM_DELETE_WINDOW", lambda: close_settings(settings_window))

    global sp_dc_entry, ip_entry, port_entry

    Label(settings_window, text="SP_DC Key:", font=("Segoe UI SemiBold", 10), bg="#222", fg="white").grid(row=0, column=0, sticky='e', padx=(10, 2), pady=10)
    sp_dc_entry = Entry(settings_window, bg="#333", fg="white", insertbackground='white', width=41)
    sp_dc_entry.grid(row=0, column=1, padx=(2, 10), pady=10)
    sp_dc_entry.insert(0, config_data.get('sp_dc', 'Enter SP_DC Key'))

    frame_ip_port = Frame(settings_window, bg="#222")
    frame_ip_port.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

    Label(frame_ip_port, text="IP:", font=("Segoe UI SemiBold", 10), bg="#222", fg="white").pack(side="left", padx=5)
    ip_entry = Entry(frame_ip_port, bg="#333", fg="white", insertbackground='white', width=15)
    ip_entry.pack(side="left", padx=(5, 10))
    ip_entry.insert(0, config_data.get('ip', '127.0.0.1'))

    Label(frame_ip_port, text="Port:", font=("Segoe UI SemiBold", 10), bg="#222", fg="white").pack(side="left", padx=5)
    port_entry = Entry(frame_ip_port, bg="#333", fg="white", insertbackground='white', width=15)
    port_entry.pack(side="left", padx=(10, 5))
    port_entry.insert(0, config_data.get('port', '9000'))

    Button(settings_window, text="Update Config", command=lambda: update_config(settings_window), bg="#333", fg="white").grid(row=2, column=0, columnspan=2, padx=10, pady=20, sticky='nsew')

def close_settings(settings_window):
    global settings_window_open
    settings_window_open = False
    settings_window.destroy()

def load_config():
    global sp_dc, ip, port
    clear_lyric()
    filename = "config.json"
    keys = ['sp_dc', 'ip', 'port']

    try:
        with open(filename, 'r') as file:
            data = json.load(file)
            values = [data.get(key) for key in keys]

            if None in values:
                update_lyric("Config file key missing")
                return
            sp_dc, ip, port = values
            update_lyric("Ready to run!")

    except FileNotFoundError:
        update_lyric("Config file missing, open settings to create one")


def update_config(settings_window):
    config_data = {
        'sp_dc': sp_dc_entry.get(),
        'ip': ip_entry.get(),
        'port': int(port_entry.get())
    }
    with open('config.json', 'w') as config_file:
        json.dump(config_data, config_file, indent=4)

    if is_running():
        toggle_start_stop()

    load_config()
    close_settings(settings_window)

def update_song(song):
    song_sync.configure(text=song)

def clear_lyric():
    lyrics.config(text="")

def update_lyric(lyric):
    lyrics.config(text=lyric)
