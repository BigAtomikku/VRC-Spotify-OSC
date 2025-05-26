import flet as ft
from flet import Colors
from core import ServiceManager
from gui import build_title_bar, Content, Settings, UpdateHandlers


class SpotifyOSCApp:
    def __init__(self, page: ft.Page):
        self.content = None
        self.settings = None
        self.bg_color = Colors.GREY_900
        self.accent_color = Colors.WHITE
        self.text_color = Colors.WHITE
        self.settings_container = None
        self.content_container = None
        self.page = page
        self.setup_window()
        self.handlers = UpdateHandlers(self)
        self.build_ui()
        self.service = ServiceManager()
        self.service.start(self.handlers)

    def setup_window(self):
        self.page.title = "VRC Lyrics"
        self.page.window.width = 450
        self.page.window.height = 500
        self.page.window.bgcolor = Colors.TRANSPARENT
        self.page.bgcolor = Colors.TRANSPARENT
        self.page.window.frameless = True
        self.page.window.maximizable = False
        self.page.window.center()

    def build_ui(self):
        self.page.controls.clear()
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(None),
            bgcolor=self.accent_color,
            behavior=ft.SnackBarBehavior.FLOATING,
            margin=ft.Margin(40, 0, 40, 365),
            duration=5000
        )
        self.page.overlay.append(self.page.snack_bar)
        self.settings = Settings(self.page, self.text_color, self.bg_color)
        self.settings_container = self.settings.build()
        self.settings_container.visible = False
        self.content = Content(self.page, self.text_color, self.bg_color, self.accent_color)
        self.content_container = self.content.build()

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
            content=ft.Column(spacing=0, controls=[
                build_title_bar(self),
                ft.Container(
                    padding=23,
                    expand=True,
                    content=ft.Stack(expand=True, controls=[self.content_container, self.settings_container])
                )
            ]),
        )

        self.page.add(layout)

    def minimize_app(self):
        self.page.window.minimized = True
        self.page.update()

    def close_app(self):
        self.service.stop()
        self.page.window.close()

    def toggle_settings(self):
        changed = 0

        if self.settings_container.visible:
            changed, message = self.settings.save_settings()
            if changed == 2:
                self.handlers.error(message)
                return

        self.settings_container.visible = not self.settings_container.visible
        self.settings_container.update()
        self.content_container.visible = not self.content_container.visible
        self.content_container.update()

        if changed == 1:
            self.service.stop()
            self.service.start(self.handlers)


def main():
    ft.app(target=SpotifyOSCApp)


if __name__ == "__main__":
    main()
