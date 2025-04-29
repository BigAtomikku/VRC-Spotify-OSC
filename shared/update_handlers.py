class UpdateHandlers:
    def __init__(self, app):
        self.app = app

    def track_info(self, title, artist, album_art=None):
        self.app.content_panel.update_track_info(title, artist, album_art)

    def progress(self, progress, duration):
        self.app.content_panel.update_progress(progress, duration)

    def lyric(self, lyric):
        self.app.content_panel.update_lyric(lyric)
