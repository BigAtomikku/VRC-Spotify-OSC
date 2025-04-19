import flet as ft
from flet import Colors, Icons


class SettingsPanel:
    def __init__(self, app):
        self.app = app

    def build(self):
        app = self.app
        config = app.config
        page = app.page
        text_color = app.text_color
        bg_color = app.bg_color
        accent_color = app.accent_color

        ip_field = ft.TextField(
            label="IP",
            value=config.get('ip', '127.0.0.1'),
            width=170,
            bgcolor=Colors.GREY_800,
            color=text_color
        )

        port_field = ft.TextField(
            label="Port",
            value=config.get('port', 9000),
            width=170,
            bgcolor=Colors.GREY_800,
            color=text_color
        )

        client_id_field = ft.TextField(
            label="Client ID",
            value=config.get('client_id', ''),
            width=350,
            bgcolor=Colors.GREY_800,
            color=text_color
        )

        def save_settings(e):
            config.set('ip', ip_field.value)
            config.set('port', port_field.value)
            config.set('client_id', client_id_field.value)
            app.service.stop()
            app.start_service()

        # Settings panel
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Settings", size=20, weight=ft.FontWeight.BOLD, color=text_color),
                    ft.Divider(color=Colors.GREY_800),

                    ft.Text("OSC Settings", size=16, weight=ft.FontWeight.BOLD, color=text_color),
                    ft.Row(
                        [
                            ip_field,
                            port_field,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),

                    ft.Text("Spotify Settings", size=16, weight=ft.FontWeight.BOLD, color=text_color),
                    client_id_field,
                    ft.Container(height=20),
                    ft.ElevatedButton(
                        "Save Settings",
                        icon=Icons.SAVE,
                        bgcolor=accent_color,
                        color=Colors.BLACK,
                        on_click=save_settings
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            padding=20,
            width=page.width,
            bgcolor=bg_color,
            border_radius=ft.border_radius.only(bottom_left=20, bottom_right=20),
            expand=True
        )
