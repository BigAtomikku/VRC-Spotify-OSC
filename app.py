import flet as ft
from flet import Colors, Icons
from config import ConfigManager
from gui.content import ContentPanel
from gui.settings import SettingsPanel
from service_manager import ServiceManager


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
        self.page.window.width = 550
        self.page.window.height = 550
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

        # Main layout
        layout = ft.Container(
            content=ft.Column([
                self.build_title_bar(),
                self.content_container,
                self.settings_container
            ], expand=True, spacing=5),
            border_radius=20,
            bgcolor=self.bg_color,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.Colors.with_opacity(0.2, Colors.BLACK),
                offset=ft.Offset(0, 2)
            )
        )

        self.page.add(layout)

    def build_title_bar(self):
        return ft.WindowDragArea(
            ft.Container(
                border_radius=ft.border_radius.only(top_left=20, top_right=20),
                bgcolor=Colors.BLACK45,
                padding=10,
                content=ft.Row([
                    ft.IconButton(
                        icon=Icons.SETTINGS,
                        icon_color=self.text_color,
                        tooltip="Settings",
                        on_click=self.toggle_settings
                    ),
                    ft.Container(
                        content=ft.Text(
                            "VRC SPOTIFY OSC",
                            size=22,
                            color=self.text_color,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER
                        ),
                        expand=True,
                        alignment=ft.alignment.center
                    ),
                    ft.IconButton(
                        icon=Icons.CLOSE,
                        icon_color=self.text_color,
                        tooltip="Close",
                        on_click=lambda e: self.page.window.close()
                    )
                ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ),
            maximizable=False
        )

    def toggle_settings(self, e):
        self.settings_visible = not self.settings_visible
        self.settings_container.visible = self.settings_visible
        self.content_container.visible = not self.settings_visible
        self.page.update()

    def start_service(self):
        client_id = self.config.get('client_id')
        ip = self.config.get('ip')
        port = self.config.get('port')

        if client_id:
            def update_track_info(title=None, artist=None, lyric=None, progress=None, duration=None, album_art=None):
                self.content_panel.update_track_info(title, artist, lyric, progress, duration, album_art)

            self.service.start(client_id, ip, port, update_track_info)


def main():
    ft.app(target=SpotifyOSCApp)


if __name__ == "__main__":
    main()
