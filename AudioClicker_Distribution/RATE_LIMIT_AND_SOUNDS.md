# Rate Limiting & Custom Sounds Guide

## 🛡️ Rate Limiting System

### What It Does
Prevents users from spamming clicks by limiting them to a maximum number of clicks per hour (default: 10 clicks/hour).

### Features
- **Cute Warning Messages**: When rate limited, users see friendly messages like:
  - "Whoa there, Alex! 💜 You've already rewarded the good boy/girl 10 times in the past hour. Give them a break!"
- **Countdown Timer**: Shows exactly when they can click again
- **Color-coded**: Rate-limited button turns orange
- **Per-User Tracking**: Each user has their own rate limit counter

### Configuration
1. **Access Admin Panel**: Press `Shift + Ctrl + A` to reveal the admin button
2. Click **🔧 Admin** button in top-left corner
3. Change "Max clicks per hour" value
4. Click **Update**

### Files Created
- `rate_limits.json` - Stores click timestamps per user

---

## 🎵 Custom Sound System

### What It Does
Allows the server owner to assign different click sounds to different users. For example:
- Partner 1 gets a bell sound
- Partner 2 gets a chime sound
- Friend gets a honk sound

### Setup

#### 1. Add Sound Files
1. Place `.wav`, `.mp3`, or `.ogg` files in the `static/sounds/` folder
2. Example structure:
   ```
   static/
   ├── click.wav (default sound)
   └── sounds/
       ├── bell.wav
       ├── chime.wav
       ├── honk.wav
       └── purr.wav
   ```

#### 2. Assign Sounds to Users
1. Press `Shift + Ctrl + A` to show admin button
2. Click **🔧 Admin**
3. In the "User Sound Assignments" section, you'll see all users who have clicked
4. Use the dropdown next to each user to assign their custom sound
5. Select "Use Default" to reset to the default click.wav

### How It Works
- When a user clicks, the server checks if they have a custom sound assigned
- If yes, plays their custom sound
- If no, plays the default `static/click.wav`
- Each user's custom sound is saved in `user_sessions.json`

### Tips
- Sound files should be short (0.5-2 seconds)
- Use .wav format for best compatibility
- Test sounds by clicking with different users

---

## 📊 Admin Panel Features

### Access
Press `Shift + Ctrl + A` on the keyboard to toggle the admin button visibility.

### Features

#### 1. Rate Limit Settings
- View current limit
- Change maximum clicks per hour
- Applies to all users immediately

#### 2. User Management
- See all users who have clicked
- View their nickname and color
- See when they last clicked
- See their current custom sound
- Assign custom sounds from dropdown

#### 3. Available Sounds
- Lists all sound files in `static/sounds/`
- Shows which sounds can be assigned

### Example Use Cases

**For Training Context:**
- Set rate limit to 10 clicks/hour to prevent over-rewarding
- Give your partner a special bell sound
- Give friends a different sound so you know who's clicking

**For Gaming/Fun:**
- Set high rate limit (50+) for active play sessions
- Assign funny sounds to different friends
- Lower rate limit at night for sleep time

---

## 🔧 Technical Details

### Rate Limiting
- Window: 1 hour (3600 seconds)
- Default limit: 10 clicks
- Stored in: `rate_limits.json`
- Tracks: timestamp of each click per user

### Custom Sounds
- Stored in: `user_sessions.json` under each user's session
- Path format: `static/sounds/filename.wav`
- Fallback: `static/click.wav` if custom sound not found

### API Endpoints
- `GET /admin/users` - List all users
- `POST /admin/user/<session_id>/sound` - Assign custom sound
- `GET /admin/sounds` - List available sound files
- `GET/POST /admin/rate-limit` - Get/set rate limit

---

## 💡 Tips

1. **Test Rate Limiting**: Try clicking rapidly to see the cute warning messages
2. **Add Fun Sounds**: Find free sound effects online (freesound.org, zapsplat.com)
3. **Backup**: Keep your `user_sessions.json` and `rate_limits.json` files safe
4. **Reset Users**: Delete `rate_limits.json` to clear all rate limit data
5. **Security**: The admin panel is hidden but not password-protected - anyone who knows the keyboard shortcut can access it

---

Enjoy your personalized clicking experience! 💜✨
