import flet as ft


class UpdateHandlers:
    def __init__(self, app):
        self.app = app

    def track_info(self, title, artist, album_art=None):
        self.app.content.update_track_info(title, artist, album_art)

    def progress(self, progress, duration):
        self.app.content.update_progress(progress, duration)

    def lyric(self, lyric):
        self.app.content.update_lyric(lyric)

    def error(self, message):
        self.app.page.snack_bar.content = ft.Text(message, color=self.app.text_color)
        self.app.page.snack_bar.bgcolor = ft.Colors.RED
        self.app.page.snack_bar.open = True
        self.app.page.update()
