# VRC Lyrics

Display your current Spotify track and synchronized lyrics in the VRChat Chatbox.

<div align="center">
   <img src="https://github.com/user-attachments/assets/9a447777-6ce6-45d2-9f3e-155aea97476d" width="33%" alt="Home Screen" />
</div>

<div align="center">
  <img src="https://github.com/user-attachments/assets/4b57ea6c-9d13-4ec3-a25a-e6f42ea83814" width="49%" alt="Home Screen" />
  <img src="https://github.com/user-attachments/assets/1a229703-560b-4c47-a9a7-8c2c6673a0f0" width="49%" alt="Settings Screen" />
</div>

You can also connect to third-party applications like TTS Voice Wizard! (requires pre-release 1.6.8.5 or above)

<div align="center">
   <img src="https://github.com/user-attachments/assets/c2654f28-4bfb-46c9-9596-42fb843a682b" width="75%" alt="TTSVoiceWizard Integration Example" />
</div>

## Installation

1. **Download the latest release:** [VRC-Lyrics.zip](https://github.com/BigAtomikku/VRC-LyricsC/releases/latest)

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
