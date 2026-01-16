# 💥 NEW FEATURES: Bonk Button & Sound Management

## What's New?

### 1. 💥 BONK Button
- New red "BONK!" button next to the click button
- Plays a custom bonk sound effect
- **Optional**: Can trigger PiShock device for physical feedback
- Perfect for playful punishment or attention-getting

### 2. ⚡ PiShock Integration
- Connect your PiShock shock collar
- Bonk button can trigger: Shock, Vibrate, or Beep
- Fully configurable intensity and duration
- Safety features built-in
- See `PISHOCK_SETUP.md` for detailed setup

### 3. 🎵 Easy Sound Management (Coming in GUI update)
- Change click sound with dropdown
- Change bonk sound with dropdown
- Preview sounds before setting
- Add custom sounds to `static/sounds/` folder

## Quick Start

### Using the Bonk Button

1. **Web Interface**:
   - Just click the red "💥 BONK!" button
   - Plays bonk sound on server
   - If PiShock enabled, also sends shock/vib/beep

2. **What Happens**:
   - Sound plays immediately
   - If PiShock configured & enabled: triggers device
   - Shows notification of success

### Setting Up PiShock (Optional)

**⚠️ IMPORTANT: Read `PISHOCK_SETUP.md` for full safety guidelines!**

**Quick Steps:**
1. Get your PiShock credentials from https://pishock.com
2. Create `pishock_config.json` with:
```json
{
  "enabled": true,
  "username": "YourUsername",
  "api_key": "your-api-key-here",
  "sharecode": "your-sharecode",
  "name": "PiShock",
  "intensity": 30,
  "duration": 1,
  "operation": 0
}
```
3. **Test safely**: Start with intensity 10-20
4. Click bonk button to test

**Operation Codes:**
- `0` = Shock ⚡
- `1` = Vibrate 📳
- `2` = Beep 🔊 (safest for testing)

### Adding Custom Sounds

1. **Get Sound Files**:
   - Download `.wav`, `.mp3`, or `.ogg` files
   - Keep files under 5MB for best performance

2. **Add to Project**:
   - Place files in `static/sounds/` folder
   - Name them clearly (e.g., `dog_bark.wav`, `bonk_cartoon.wav`)

3. **Set as Default** (via API for now, GUI coming soon):
   ```bash
   # Click sound
   curl -X POST http://localhost:5000/admin/sounds/set-default \
     -H "Content-Type: application/json" \
     -d '{"click_sound": "your_sound.wav"}'
   
   # Bonk sound
   curl -X POST http://localhost:5000/admin/sounds/set-default \
     -H "Content-Type: application/json" \
     -d '{"bonk_sound": "bonk_cartoon.wav"}'
   ```

## API Endpoints

### New Bonk Endpoint
```
POST /bonk
Body: { "nickname": "YourName" }
Response: { "success": true, "pishock_triggered": false }
```

### PiShock Management
```
GET /admin/pishock          # Get current config
POST /admin/pishock         # Update config
POST /admin/pishock/test    # Test device
```

### Sound Management
```
GET /admin/sounds           # List available sounds
POST /admin/sounds/set-default  # Set default sounds
```

## Safety & Best Practices

### PiShock Safety
- ✅ **Always start with LOW intensity** (10-20)
- ✅ **Test on yourself first**
- ✅ **Have a safe word/gesture**
- ✅ **Keep device charged**
- ✅ **Check skin regularly** for irritation
- ❌ **Never leave unattended**
- ❌ **Don't use while sleeping**
- ❌ **Don't exceed 50 intensity** without experience

### Sound Guidelines
- Keep volume reasonable
- Test sounds before use
- Avoid extremely loud files
- Respect sound copyright

## Troubleshooting

### Bonk button doesn't work
- Check browser console for errors
- Verify `/bonk` endpoint in app.py
- Make sure server is running

### PiShock not triggering
1. Check `pishock_config.json` exists
2. Verify `"enabled": true`
3. Test credentials on PiShock website first
4. Check internet connection
5. Try `/admin/pishock/test` endpoint

### Sound doesn't play
- Verify file exists in `static/sounds/`
- Check file format (.wav, .mp3, .ogg)
- Try different sound file
- Check server logs for errors

### Can't find bonk sound file
Default location: `static/bonk.wav`

If missing:
1. Add any `.wav` file as `static/bonk.wav`
2. Or use API to set different sound
3. Falls back to system beeps if not found

## Coming Soon in GUI

The GUI server will be updated with:
- ⚡ PiShock configuration panel
- 🎵 Sound selection dropdowns
- 🔊 Sound preview buttons
- 📊 Bonk statistics
- ⚙️ Easy settings management

## Need Help?

1. **PiShock Setup**: Read `PISHOCK_SETUP.md`
2. **General Issues**: Check server console for errors
3. **Sound Problems**: Verify files in `static/sounds/`
4. **API Testing**: Use tools like Postman or curl

## Examples

### Safe PiShock Testing Config
```json
{
  "enabled": true,
  "username": "yourname",
  "api_key": "your-key",
  "sharecode": "SHARECODE123",
  "name": "PiShock",
  "intensity": 15,
  "duration": 1,
  "operation": 2
}
```
(Operation 2 = beep only, safest test)

### Recommended Sound Sites
- freesound.org (Creative Commons sounds)
- zapsplat.com (Free sound effects)
- soundbible.com (Public domain sounds)

Remember: **Safety and Consent First!** 💜

---

Enjoy your new bonk button responsibly! 💥⚡
