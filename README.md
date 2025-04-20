# VRC Spotify OSC

Display your current Spotify track and synchronized lyrics in the VRChat Chatbox.

![VRChat display of song information](https://github.com/BigAtomikku/VRC-Spotify-OSC/assets/51969732/d1a2b873-9154-4a92-8755-1746c58a23c6)

You can also connect to third-party applications like TTS Voice Wizard! (requires pre-release 1.6.8.5)

![TTS Voice Wizard integration](https://github.com/BigAtomikku/VRC-Spotify-OSC/assets/51969732/1cbd8c0f-fb3a-4698-aa34-6f6cd32d96e7)

## Installation

1. **Download the latest release:** [VRC-Spotify-OSC.zip](https://github.com/BigAtomikku/VRC-Spotify-OSC/releases/latest/download/VRC-Spotify-OSC.zip)

2. **Run the program**

3. **Configure Settings**
   - Open the settings menu
   - Set IP address (default: 127.0.0.1)
   - Configure Port:
     - 9000 for VRChat Chatbox (default)
     - 4026 for TTS Voice Wizard integration

4. **Set Up Spotify Connection**

   **Option A: Using Spotify Provider**
   - Visit [Spotify's website](https://open.spotify.com)
   - [Find your sp_dc cookie](https://github.com/akashrchandran/syrics/wiki/Finding-sp_dc) value
   - Copy and paste this value into the SP_DC field

   **Option B: Using LRCLib Provider**
   - Create a Spotify Developer App:
     - Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
     - Create a new app
     - Add `http://127.0.0.1:5000/callback` as a **Redirect URI** in app settings
   - Copy the generated Client ID
   - Paste your Client ID into the settings

5. **Click "Save Settings" to apply your configuration**

## Known Issues

- Fast-paced lyrics may time-out the VRChat chatbox. Check if you're timed out by opening the launch pad.

## Support

If you encounter any issues or have questions, please open an issue on GitHub.