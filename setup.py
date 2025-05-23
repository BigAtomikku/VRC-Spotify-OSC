from cx_Freeze import setup, Executable

build_exe_options = {
    "excludes": [
            "winsdk.windows.applicationmodel", "winsdk.windows.data", "winsdk.windows.devices",
            "winsdk.windows.globalization", "winsdk.windows.graphics", "winsdk.windows.networking",
            "winsdk.windows.security", "winsdk.windows.storage", "winsdk.windows.system", "winsdk.windows.ui",
            "winsdk.windows.web",
            "anyio", "h11", "oauthlib", "sniffio", "typing_extensions"
        ]
}

setup(
    name="VRC Lyrics",
    version="2.1.0",
    description="VRC Lyrics OSC Controller",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            script="app.py",
            base="Win32GUI",
            target_name="VRC Lyrics.exe",
            icon="assets/icon.ico",
            copyright="Copyright (C) 2025 Atomikku. All rights reserved.",
        )
    ]
)
