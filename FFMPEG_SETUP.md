# FFmpeg Setup for Voice Message Support

## Why FFmpeg?

The voice messages recorded on mobile devices are typically in **WebM** or **MP4** format, which pygame cannot play directly. FFmpeg automatically converts these to **WAV** format for playback on the server.

## Quick Install (Windows)

### Option 1: Chocolatey (Easiest)
If you have Chocolatey package manager:
```powershell
choco install ffmpeg
```

### Option 2: Scoop
If you have Scoop package manager:
```powershell
scoop install ffmpeg
```

### Option 3: Manual Download
1. Download ffmpeg from: https://www.gyan.dev/ffmpeg/builds/
2. Download the "ffmpeg-release-essentials.zip"
3. Extract to `C:\ffmpeg`
4. Add to PATH:
   - Open "Environment Variables" in Windows settings
   - Edit "Path" under System Variables
   - Add `C:\ffmpeg\bin`
   - Click OK
5. Restart your terminal/command prompt
6. Test: `ffmpeg -version`

## Verification

After installing, restart your Flask server and try recording a voice message. You should see:
```
🔄 Converting static\voice_message.webm to WAV using ffmpeg...
✅ Converted to WAV: static\voice_message_converted.wav
✅ Played converted WAV file
```

## Without FFmpeg

If you don't install ffmpeg, the app will still work but:
- Voice messages may not play (depending on format)
- You'll see: `⚠️ ffmpeg not found on system`
- The app will try pygame and winsound as fallbacks

## Troubleshooting

**"ffmpeg not found"**
- Make sure ffmpeg is in your PATH
- Restart terminal after adding to PATH
- Try running `ffmpeg -version` in terminal

**"Access is denied"**
- Run PowerShell as Administrator when installing
- Check antivirus isn't blocking ffmpeg

**Still not working?**
- Check the Flask console logs for detailed error messages
- The app will show which conversion method succeeded/failed
