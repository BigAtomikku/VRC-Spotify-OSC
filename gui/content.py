import flet as ft
from flet import Colors, Icons


class ContentPanel:
    def __init__(self, app):
        self.app = app
        self.lyrics_text = None
        self.time_info = None
        self.progress_bar = None
        self.artist = None
        self.song_title = None
        self.album_art = None

    def build(self):
        app = self.app
        page = app.page
        text_color = app.text_color
        bg_color = app.bg_color
        accent_color = app.accent_color

        self.song_title = ft.Text(
            "Song Title",
            size=24,
            weight=ft.FontWeight.BOLD,
            color=text_color,
            text_align=ft.TextAlign.CENTER,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
            width=500
        )

        self.artist = ft.Text(
            "Artist Name",
            size=18,
            color=Colors.GREY_300,
            text_align=ft.TextAlign.CENTER
        )

        self.progress_bar = ft.ProgressBar(
            width=350,
            value=0.0,
            color=accent_color,
            bgcolor=Colors.GREY_800
        )

        self.time_info = ft.Row(
            [
                ft.Text("0:00", size=12, color=Colors.GREY_300),
                ft.Text("0:00", size=12, color=Colors.GREY_300)
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            width=350
        )

        self.lyrics_text = ft.Text(
            "Lyrics will appear here...",
            size=15,
            color=text_color,
            text_align=ft.TextAlign.CENTER,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
            weight=ft.FontWeight.BOLD
        )

        lyrics_container = ft.Container(
            content=self.lyrics_text,
            width=500,
            height=50,
            border_radius=10,
            bgcolor=Colors.GREY_800,
            padding=10,
            alignment=ft.alignment.center
        )

        self.album_art = ft.Image(
            src="https://upload.wikimedia.org/wikipedia/commons/8/89/Portrait_Placeholder.png?20170328184010",
            width=150,
            height=150,
            fit=ft.ImageFit.COVER,
            border_radius=10
        )

        return ft.Container(
            content=ft.Column(
                [
                    self.album_art,
                    ft.Container(height=15),
                    self.song_title,
                    self.artist,
                    ft.Container(height=20),
                    self.progress_bar,
                    self.time_info,
                    ft.Container(height=10),
                    lyrics_container
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.START,
                spacing=5
            ),
            padding=20,
            width=page.width,
            bgcolor=bg_color,
            border_radius=ft.border_radius.only(bottom_left=20, bottom_right=20)
        )

    def update_track_info(self, title=None, artist=None, lyric=None, progress=None, duration=None, album_art=None):
        if title is not None:
            self.song_title.value = title
        if artist is not None:
            self.artist.value = artist
        if lyric is not None:
            self.lyrics_text.value = lyric

        if album_art is not None:
            self.album_art.src = album_art

        if progress is not None and duration is not None:
            progress_seconds = progress / 1000.0
            duration_seconds = duration / 1000.0

            if duration_seconds > 0:
                self.progress_bar.value = progress_seconds / duration_seconds
                current_time = format_time(progress_seconds)
                total_time = format_time(duration_seconds)
                self.time_info.controls[0].value = current_time
                self.time_info.controls[1].value = total_time

        self.app.page.update()


def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02}:{seconds:02}"
