import flet as ft
from gui import ContentPanel
from gui import SettingsPanel
from flet import Colors, Icons
from core import ServiceManager
from config import ConfigManager


class SpotifyOSCApp:
    def __init__(self, page: ft.Page):
        self.content_panel = None
        self.bg_color = Colors.GREY_900
        self.accent_color = Colors.GREEN_500
        self.text_color = Colors.WHITE
        self.settings_container = None
        self.content_container = None
        self.page = page
        self.config = ConfigManager()
        self.settings_visible = False
        self.setup_window()
        self.build_ui()
        self.service = ServiceManager()
        self.start_service()

    def setup_window(self):
        self.page.title = "VRC Lyrics"
        self.page.window.width = 500
        self.page.window.height = 500
        self.page.window.bgcolor = Colors.TRANSPARENT
        self.page.bgcolor = Colors.TRANSPARENT
        self.page.window.frameless = True
        self.page.window.maximizable = False
        self.page.window.center()

    def build_ui(self):
        self.content_panel = ContentPanel(self)
        self.content_container = self.content_panel.build()
        self.settings_container = SettingsPanel(self).build()
        self.settings_container.visible = False

        layout = ft.Container(
            expand=True,
            border_radius=20,
            bgcolor=self.bg_color,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.Colors.with_opacity(0.2, Colors.BLACK),
                offset=ft.Offset(0, 2)
            ),
            content=ft.Column([
                self.build_title_bar(),
                self.content_container,
                self.settings_container
            ]),
        )

        self.page.add(layout)

    def build_title_bar(self):
        return ft.WindowDragArea(
            maximizable=False,
            content=ft.Container(
                bgcolor=Colors.BLACK45,
                padding=10,
                content=ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            expand=True,
                            alignment=ft.alignment.center_left,
                            content=ft.IconButton(
                                icon=Icons.SETTINGS,
                                icon_color=self.text_color,
                                tooltip="Settings",
                                on_click=lambda e: self.toggle_settings()
                            )
                        ),

                        ft.Container(
                            expand=True,
                            alignment=ft.alignment.center,
                            content=ft.Text(
                                "VRC LYRICS",
                                size=22,
                                color=self.text_color,
                                weight=ft.FontWeight.BOLD,
                                text_align=ft.TextAlign.CENTER
                            )
                        ),

                        ft.Container(
                            expand=True,
                            alignment=ft.alignment.center_right,
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.END,
                                controls=[
                                    ft.IconButton(
                                        icon=Icons.REMOVE,
                                        icon_color=self.text_color,
                                        tooltip="Minimize",
                                        on_click=lambda e: self.minimize_app()
                                    ),
                                    ft.IconButton(
                                        icon=Icons.CLOSE,
                                        icon_color=self.text_color,
                                        tooltip="Close",
                                        on_click=lambda e: self.close_app()
                                    )
                                ]
                            )
                        )
                    ]
                )
            )
        )

    def minimize_app(self):
        self.page.window.minimized = True
        self.page.update()

    def close_app(self):
        self.service.stop()
        self.page.window.close()

    def toggle_settings(self):
        self.settings_visible = not self.settings_visible
        self.settings_container.visible = self.settings_visible
        self.content_container.visible = not self.settings_visible
        self.page.update()

    def start_service(self):
        provider = self.config.get('provider')

        if provider == "Spotify":
            key = self.config.get('sp_dc')
        else:
            key = self.config.get('client_id')

        ip = self.config.get('ip')
        port = self.config.get('port')

        if key:
            def update_track_info(title=None, artist=None, lyric=None, progress=None, duration=None, album_art=None):
                self.content_panel.update_track_info(title, artist, lyric, progress, duration, album_art)

            self.service.start(provider, key, ip, port, update_track_info)


def main():
    ft.app(target=SpotifyOSCApp)


if __name__ == "__main__":
    main()
