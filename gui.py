from tkinter import Label, Tk, Text, Button, OptionMenu, StringVar

def start_gui():
    window = Tk()
    window.title("VRC Spotify OSC v2.0.0")
    window.geometry("400x100")
    window.configure(bg="#222")
    window.resizable(False, False)

    global name_sync
    name_sync = Label(window, text="", font=("Helvetica", 15), bg="#222", fg="white")
    name_sync.pack(padx=10, pady=10)

    global lyric_sync
    lyric_sync = Label(window, text="", font=("Helvetica", 13), bg="#222", fg="white")
    lyric_sync.pack(padx=10, pady=10)

    window.mainloop()

def update_song(name, artist):
    name_sync.configure(text=name + " - " + artist)

def update_lyric(lyric):
    lyric_sync.config(text=lyric)
