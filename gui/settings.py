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
        form_color = Colors.GREY_800

        ip_field = ft.TextField(
            label="IP",
            value=config.get('ip', '127.0.0.1'),
            width=170,
            bgcolor=form_color,
            color=text_color
        )

        port_field = ft.TextField(
            label="Port",
            value=config.get('port', 9000),
            width=170,
            bgcolor=form_color,
            color=text_color
        )

        lyric_provider_dropdown = ft.DropdownM2(
            label="Lyric Provider",
            value=config.get('provider'),
            options=[
                ft.dropdown.Option("Spotify"),
                ft.dropdown.Option("LRCLibAPI"),
            ],
            width=350,
            bgcolor=form_color,
            color=text_color
        )

        client_id_field = ft.TextField(
            label="Client ID",
            value=config.get('client_id', ''),
            width=350,
            bgcolor=form_color,
            color=text_color,
            visible=config.get('lyric_provider') == 'LRCLibAPI'
        )

        sp_dc_field = ft.TextField(
            label="SP_DC",
            value=config.get('sp_dc', ''),
            width=350,
            bgcolor=form_color,
            color=text_color,
            visible=config.get('lyric_provider') == 'Spotify'
        )

        def update_provider_fields():
            match lyric_provider_dropdown.value:
                case 'Spotify':
                    client_id_field.visible = False
                    sp_dc_field.visible = True
                case 'LRCLibAPI':
                    client_id_field.visible = True
                    sp_dc_field.visible = False
            page.update()

        update_provider_fields()
        lyric_provider_dropdown.on_change = lambda e: update_provider_fields()

        def save_settings():
            config.set('ip', ip_field.value)
            config.set('port', int(port_field.value))
            config.set('provider', lyric_provider_dropdown.value)
            match lyric_provider_dropdown.value:
                case 'Spotify': config.set('sp_dc', sp_dc_field.value)
                case 'LRCLibAPI': config.set('client_id', client_id_field.value)
            app.service.stop()
            app.start_service()

        # Settings panel
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("OSC Settings", size=16, weight=ft.FontWeight.BOLD, color=text_color),
                    ft.Row(
                        [
                            ip_field,
                            port_field,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),

                    ft.Divider(color=Colors.GREY_800),

                    ft.Text("Lyrics Settings", size=16, weight=ft.FontWeight.BOLD, color=text_color),
                    lyric_provider_dropdown,
                    client_id_field,
                    sp_dc_field,

                    ft.Container(height=10),

                    ft.ElevatedButton(
                        "Save Settings",
                        icon=Icons.SAVE,
                        bgcolor=accent_color,
                        color=Colors.BLACK,
                        on_click=lambda e: save_settings()
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
            ),
            padding=20,
            width=page.width,
            bgcolor=bg_color,
            border_radius=ft.border_radius.only(bottom_left=20, bottom_right=20),
        )
