from syrics.api import Spotify
import syrics.exceptions
import gui
import time

# Connect to spotify (via syrics)
def connect_to_spotify(sp_dc):
    try:
        return Spotify(sp_dc)
    except syrics.exceptions.NotValidSp_Dc:
        gui.toggle_start_stop()
        gui.update_lyric("sp_dc key invalid, please check it and update settings")
        return None


# Returns array of data for current song
def current_data(sp):
    data = sp.get_current_song()

    try:
        song_info = {
            'uri': data['item']['id'],
            'name': data['item']['name'],
            'artist': data['item']['artists'][0]['name'],
            'progress_ms': data['progress_ms'],
            'is_playing': data['is_playing']
        }
        return song_info
    except (TypeError, KeyError):
        return None


# Returns dictionary of times associated with lyrics
def lyrics_dictionary(data):
    lyrics_data = data['lyrics']['lines']
    lyrics_dic = {int(line['startTimeMs']): line['words'] for line in lyrics_data}
    return lyrics_dic


def spotify_thread(sp_dc, song_data_queue, running):
    sp = connect_to_spotify(sp_dc)
    current_song_id = ""

    while running.is_set():
        try:
            current_song = current_data(sp)

            if current_song is None:
                time.sleep(1)
                continue

            song_data_queue.put({'type': 'update', 'song_info': current_song})

            # Check if the song has changed
            song_id = current_song['uri']
            if song_id != current_song_id:
                current_song_id = song_id
                lyrics_data = sp.get_lyrics(song_id)

                if lyrics_data is None:
                    song_data_queue.put({'type': 'no_lyrics'})
                else:
                    lyrics = lyrics_dictionary(lyrics_data)
                    song_data_queue.put({'type': 'new_lyrics', 'lyrics': lyrics})

            # Sleep to reduce API calls
            time.sleep(0.25)

        except syrics.exceptions.NoSongPlaying:
            print("Access token expired, reconnecting")
            sp = connect_to_spotify(sp_dc)