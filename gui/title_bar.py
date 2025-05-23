import flet as ft
from flet import Colors, Icons


def build_title_bar(app):
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
                            icon_color=app.text_color,
                            tooltip="Settings",
                            on_click=lambda e: app.toggle_settings()
                        )
                    ),

                    ft.Container(
                        expand=True,
                        alignment=ft.alignment.center,
                        content=ft.Text(
                            "VRC LYRICS",
                            size=22,
                            color=app.text_color,
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
                                    icon_color=app.text_color,
                                    tooltip="Minimize",
                                    on_click=lambda e: app.minimize_app()
                                ),
                                ft.IconButton(
                                    icon=Icons.CLOSE,
                                    icon_color=app.text_color,
                                    tooltip="Close",
                                    on_click=lambda e: app.close_app()
                                )
                            ]
                        )
                    )
                ]
            )
        )
    )
