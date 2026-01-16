from flask import Flask, render_template, jsonify, request, send_from_directory, session
import pygame
import threading
import os
import time
import json
from pathlib import Path
from pythonosc import udp_client
from pythonosc.dispatcher import Dispatcher
import asyncio
import socket
from datetime import datetime, date
import secrets
import hashlib
import subprocess
import sys

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # Secure session key

# Add middleware to handle ngrok browser warning bypass
@app.before_request
def before_request():
    """Add headers to bypass ngrok browser warning"""
    pass

@app.after_request
def after_request(response):
    """Add headers to bypass ngrok browser warning"""
    # Add header to bypass ngrok warning page
    response.headers['ngrok-skip-browser-warning'] = 'true'
    # Also add CORS headers for API access
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, ngrok-skip-browser-warning'
    return response

# Initialize pygame mixer for audio playback
pygame.mixer.init()

# Default sound file path - you can change this or add more sounds
SOUND_FILE = "static/click.wav"  # Place a sound file here or use system beep
BONK_SOUND_FILE = "static/bonk.wav"  # Bonk sound effect
STATS_FILE = "click_stats.json"  # Persistent statistics storage
SETTINGS_FILE = "user_settings.json"  # User customization settings
VOICE_MESSAGE_DIR = "static"  # Directory for voice messages
VOICE_MESSAGE_BASE = "voice_message"  # Base filename (extension added dynamically)
CHAT_FILE = "chat_messages.json"  # Chat messages storage
SESSIONS_FILE = "user_sessions.json"  # Session-to-nickname mapping
RATE_LIMITS_FILE = "rate_limits.json"  # Rate limiting data
PISHOCK_CONFIG_FILE = "pishock_config.json"  # PiShock API configuration

# Rate limiting configuration
MAX_CLICKS_PER_HOUR = 10  # Default: 10 clicks per hour
RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds

# PiShock Configuration
PISHOCK_API_URL = "https://do.pishock.com/api/apioperate"

# VRChat OSC Configuration
VRCHAT_OSC_IP = "127.0.0.1"
VRCHAT_OSC_PORT = 9000
OSC_RECEIVE_PORT = 9001

# Ngrok Configuration - ADD YOUR TOKEN HERE!
NGROK_AUTH_TOKEN = ""  # Paste your ngrok token between the quotes
# Get your token from: https://dashboard.ngrok.com/get-started/your-authtoken

# Optional tunnel support
try:
    from pyngrok import ngrok, conf
    NGROK_AVAILABLE = True
except ImportError:
    NGROK_AVAILABLE = False

# OSC Client for sending to VRChat
osc_client = None
public_tunnel_url = None

def setup_tunnel():
    """Set up public tunnel if ngrok is available"""
    global public_tunnel_url
    
    if NGROK_AVAILABLE and NGROK_AUTH_TOKEN:
        try:
            # Set auth token if provided
            print("🔐 Configuring ngrok with your auth token...")
            ngrok.set_auth_token(NGROK_AUTH_TOKEN)
            
            print("🌐 Setting up public tunnel with ngrok...")
            # Note: This should be called AFTER Flask starts listening
            tunnel = ngrok.connect(5000, bind_tls=True)
            public_tunnel_url = tunnel.public_url
            print(f"✅ Public tunnel ready: {public_tunnel_url}")
            print(f"🌍 Share this URL with friends: {public_tunnel_url}")
            print("💡 Friends won't see ngrok warning page - direct access!")
            return True
        except Exception as e:
            print(f"⚠️ Ngrok setup failed: {e}")
            print(f"   Error details: {type(e).__name__}")
            print("💡 To fix: Sign up at https://ngrok.com and get your auth token")
            print("   Then add your token to NGROK_AUTH_TOKEN in app.py")
            return False
    elif NGROK_AVAILABLE and not NGROK_AUTH_TOKEN:
        print("⚠️ Ngrok is installed but no auth token provided")
        print("💡 Add your ngrok auth token to NGROK_AUTH_TOKEN in app.py")
        print("   Get your token from: https://dashboard.ngrok.com/get-started/your-authtoken")
        return False
    else:
        print("⚠️ Ngrok not installed - using local network only")
        print("💡 To enable public access, install with: pip install pyngrok")
        return False

def init_osc():
    """Initialize OSC client for VRChat communication"""
    global osc_client
    try:
        osc_client = udp_client.SimpleUDPClient(VRCHAT_OSC_IP, VRCHAT_OSC_PORT)
        print(f"🎮 OSC Client initialized for VRChat at {VRCHAT_OSC_IP}:{VRCHAT_OSC_PORT}")
        return True
    except Exception as e:
        print(f"❌ OSC initialization failed: {e}")
        return False

class AudioClicker:
    def __init__(self):
        self.click_count = 0
        self.daily_click_count = 0
        self.last_click_time = None
        self.vrchat_connected = False
        self.click_history = []  # Store last 10 clicks
        self.current_date = str(date.today())
        self.load_stats()
        
    def load_stats(self):
        """Load statistics from JSON file"""
        try:
            if os.path.exists(STATS_FILE):
                with open(STATS_FILE, 'r') as f:
                    data = json.load(f)
                    self.click_count = data.get('total_clicks', 0)
                    self.click_history = data.get('click_history', [])[-10:]  # Last 10
                    
                    # Check if date changed - reset daily count
                    saved_date = data.get('current_date', str(date.today()))
                    if saved_date == str(date.today()):
                        self.daily_click_count = data.get('daily_clicks', 0)
                    else:
                        self.daily_click_count = 0
                        self.current_date = str(date.today())
                    
                    print(f"📊 Loaded stats: {self.click_count} total clicks, {self.daily_click_count} today")
        except Exception as e:
            print(f"⚠️ Could not load stats: {e}")
    
    def save_stats(self):
        """Save statistics to JSON file"""
        try:
            data = {
                'total_clicks': self.click_count,
                'daily_clicks': self.daily_click_count,
                'current_date': self.current_date,
                'click_history': self.click_history[-10:],  # Keep last 10
                'last_updated': time.time()
            }
            with open(STATS_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save stats: {e}")
        
    def play_sound(self, sound_type="default", session_id=None, nickname=None):
        """Play different types of sounds"""
        try:
            # Check if date changed - reset daily count
            if self.current_date != str(date.today()):
                self.daily_click_count = 0
                self.current_date = str(date.today())
                print("📅 New day! Daily click count reset.")
            
            # Get custom sound for this user or use default
            sound_file = get_custom_sound_for_user(session_id) if session_id else SOUND_FILE
            
            if os.path.exists(sound_file):
                # Play custom sound file
                pygame.mixer.Sound(sound_file).play()
                print(f"🎵 Playing custom sound: {sound_file}")
            else:
                # Fall back to system beep
                import winsound
                winsound.Beep(800, 200)  # frequency, duration
                print("🔊 Playing system beep")
            
            # Update counts
            self.click_count += 1
            self.daily_click_count += 1
            self.last_click_time = time.time()
            
            # Add to click history with user info
            click_record = {
                'timestamp': self.last_click_time,
                'total_count': self.click_count,
                'daily_count': self.daily_click_count,
                'session_id': session_id,
                'nickname': nickname
            }
            self.click_history.append(click_record)
            if len(self.click_history) > 10:
                self.click_history = self.click_history[-10:]
            
            print(f"🖱️ Click #{self.click_count} triggered! (Daily: {self.daily_click_count}) by {nickname or 'Anonymous'}")
            
            # Save stats after each click
            self.save_stats()
            
            # Send OSC message to VRChat if connected
            self.send_vrchat_trigger(sound_type)
            
        except Exception as e:
            print(f"❌ Audio error: {e}")
            # Emergency fallback - print bell character
            print("\a")  # ASCII bell character
    
    def send_vrchat_trigger(self, trigger_type="click"):
        """Send OSC message to VRChat to trigger avatar reactions"""
        if osc_client:
            try:
                # Common VRChat avatar parameter paths
                # These can be customized based on your avatar setup
                
                # Trigger a boolean parameter (momentary)
                osc_client.send_message(f"/avatar/parameters/RemoteClick", True)
                
                # Send click count as integer
                osc_client.send_message(f"/avatar/parameters/ClickCount", self.click_count)
                
                # Send different trigger types
                if trigger_type == "click":
                    osc_client.send_message(f"/avatar/parameters/ClickTrigger", True)
                elif trigger_type == "special":
                    osc_client.send_message(f"/avatar/parameters/SpecialTrigger", True)
                
                # Reset the boolean after a short delay
                def reset_trigger():
                    time.sleep(0.1)
                    osc_client.send_message(f"/avatar/parameters/RemoteClick", False)
                    osc_client.send_message(f"/avatar/parameters/ClickTrigger", False)
                    osc_client.send_message(f"/avatar/parameters/SpecialTrigger", False)
                
                threading.Thread(target=reset_trigger).start()
                print(f"📡 OSC message sent to VRChat: {trigger_type}")
                self.vrchat_connected = True
                
            except Exception as e:
                print(f"❌ OSC send failed: {e}")
                self.vrchat_connected = False

# Global clicker instance
clicker = AudioClicker()

def load_sessions():
    """Load session-to-nickname mappings"""
    try:
        if os.path.exists(SESSIONS_FILE):
            with open(SESSIONS_FILE, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"⚠️ Could not load sessions: {e}")
        return {}

def save_sessions(sessions):
    """Save session-to-nickname mappings"""
    try:
        with open(SESSIONS_FILE, 'w') as f:
            json.dump(sessions, f, indent=2)
    except Exception as e:
        print(f"⚠️ Could not save sessions: {e}")

def get_or_create_session_id():
    """Get existing session ID or create a new one"""
    if 'user_id' not in session:
        session['user_id'] = secrets.token_hex(16)
    return session['user_id']

def get_user_nickname(session_id=None):
    """Get nickname for a session ID"""
    if session_id is None:
        session_id = get_or_create_session_id()
    
    sessions = load_sessions()
    return sessions.get(session_id, {}).get('nickname', None)

def set_user_nickname(nickname, session_id=None):
    """Set nickname for a session ID"""
    if session_id is None:
        session_id = get_or_create_session_id()
    
    sessions = load_sessions()
    
    # Assign a color if this is a new user
    if session_id not in sessions:
        colors = ['💜', '💙', '💚', '💛', '🧡', '❤️', '💗', '💕']
        # Use hash of session_id to consistently assign a color
        color_index = int(hashlib.md5(session_id.encode()).hexdigest(), 16) % len(colors)
        color = colors[color_index]
    else:
        color = sessions[session_id].get('color', '💜')
    
    sessions[session_id] = {
        'nickname': nickname,
        'color': color,
        'last_seen': time.time()
    }
    save_sessions(sessions)
    return color

def load_rate_limits():
    """Load rate limiting data"""
    try:
        if os.path.exists(RATE_LIMITS_FILE):
            with open(RATE_LIMITS_FILE, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"⚠️ Could not load rate limits: {e}")
        return {}

def save_rate_limits(limits):
    """Save rate limiting data"""
    try:
        with open(RATE_LIMITS_FILE, 'w') as f:
            json.dump(limits, f, indent=2)
    except Exception as e:
        print(f"⚠️ Could not save rate limits: {e}")

def check_rate_limit(session_id, nickname=None):
    """Check if user is within rate limit. Returns (allowed, wait_time, click_count)"""
    limits = load_rate_limits()
    current_time = time.time()
    
    # Get user's click history
    if session_id not in limits:
        limits[session_id] = {'clicks': []}
    
    user_limits = limits[session_id]
    
    # Remove clicks older than the rate limit window
    user_limits['clicks'] = [
        click_time for click_time in user_limits['clicks']
        if current_time - click_time < RATE_LIMIT_WINDOW
    ]
    
    click_count = len(user_limits['clicks'])
    
    # Check if user exceeded limit
    if click_count >= MAX_CLICKS_PER_HOUR:
        # Calculate when they can click again
        oldest_click = min(user_limits['clicks'])
        wait_time = int(RATE_LIMIT_WINDOW - (current_time - oldest_click))
        return False, wait_time, click_count
    
    return True, 0, click_count

def record_click_for_rate_limit(session_id):
    """Record a click for rate limiting"""
    limits = load_rate_limits()
    current_time = time.time()
    
    if session_id not in limits:
        limits[session_id] = {'clicks': []}
    
    limits[session_id]['clicks'].append(current_time)
    save_rate_limits(limits)

def get_custom_sound_for_user(session_id):
    """Get custom sound file for a specific user"""
    sessions = load_sessions()
    user_data = sessions.get(session_id, {})
    custom_sound = user_data.get('custom_sound', None)
    
    if custom_sound and os.path.exists(custom_sound):
        return custom_sound
    return SOUND_FILE

def set_custom_sound_for_user(session_id, sound_filename):
    """Set custom sound file for a specific user"""
    sessions = load_sessions()
    
    if session_id not in sessions:
        return False
    
    sound_path = f"static/sounds/{sound_filename}"
    if os.path.exists(sound_path):
        sessions[session_id]['custom_sound'] = sound_path
        save_sessions(sessions)
        return True
    return False

def get_voice_message_path():
    """Find the voice message file regardless of extension"""
    for ext in ['.webm', '.mp4', '.ogg', '.wav']:
        path = os.path.join(VOICE_MESSAGE_DIR, f"{VOICE_MESSAGE_BASE}{ext}")
        if os.path.exists(path):
            return path
    return None

def delete_all_voice_messages():
    """Delete all voice message files"""
    for ext in ['.webm', '.mp4', '.ogg', '.wav', '_converted.wav']:
        path = os.path.join(VOICE_MESSAGE_DIR, f"{VOICE_MESSAGE_BASE}{ext}")
        if os.path.exists(path):
            try:
                os.remove(path)
                print(f"🗑️ Deleted {path}")
            except Exception as e:
                print(f"⚠️ Could not delete {path}: {e}")

def convert_to_wav(input_path):
    """
    Convert audio file to WAV format for pygame compatibility.
    Returns the path to the converted WAV file, or None if conversion fails.
    """
    output_path = os.path.join(VOICE_MESSAGE_DIR, f"{VOICE_MESSAGE_BASE}_converted.wav")
    
    # Try using ffmpeg (if installed)
    try:
        print(f"🔄 Converting {input_path} to WAV using ffmpeg...")
        result = subprocess.run(
            ['ffmpeg', '-i', input_path, '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '2', '-y', output_path],
            capture_output=True,
            timeout=10
        )
        if result.returncode == 0 and os.path.exists(output_path):
            print(f"✅ Converted to WAV: {output_path}")
            return output_path
        else:
            print(f"⚠️ ffmpeg failed: {result.stderr.decode()}")
    except FileNotFoundError:
        print("⚠️ ffmpeg not found on system")
    except Exception as e:
        print(f"⚠️ ffmpeg conversion error: {e}")
    
    return None

def play_audio_file(file_path):
    """
    Play audio file using the best available method.
    Returns True if successful, False otherwise.
    """
    # Try pygame.mixer.music first (supports more formats on some systems)
    try:
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        print(f"✅ Played audio using pygame.mixer.music")
        return True
    except Exception as e:
        print(f"⚠️ pygame.mixer.music failed: {e}")
    
    # If webm/mp4, try converting to WAV first
    if file_path.endswith(('.webm', '.mp4', '.ogg')):
        converted_path = convert_to_wav(file_path)
        if converted_path:
            try:
                pygame.mixer.Sound(converted_path).play()
                # Wait for sound to finish
                while pygame.mixer.get_busy():
                    time.sleep(0.1)
                print(f"✅ Played converted WAV file")
                return True
            except Exception as e:
                print(f"⚠️ Failed to play converted WAV: {e}")
    
    # Last resort: try Windows winsound (WAV only)
    if sys.platform == 'win32' and file_path.endswith('.wav'):
        try:
            import winsound
            winsound.PlaySound(file_path, winsound.SND_FILENAME)
            print(f"✅ Played audio using winsound")
            return True
        except Exception as e:
            print(f"⚠️ winsound failed: {e}")
    
    print(f"❌ All playback methods failed for {file_path}")
    return False

def load_pishock_config():
    """Load PiShock configuration"""
    try:
        if os.path.exists(PISHOCK_CONFIG_FILE):
            with open(PISHOCK_CONFIG_FILE, 'r') as f:
                return json.load(f)
        return {
            'enabled': False,
            'username': '',
            'api_key': '',
            'sharecode': '',
            'name': 'PiShock',
            'intensity': 30,
            'duration': 1,
            'operation': 0  # 0=shock, 1=vibrate, 2=beep
        }
    except Exception as e:
        print(f"⚠️ Could not load PiShock config: {e}")
        return {'enabled': False}

def save_pishock_config(config):
    """Save PiShock configuration"""
    try:
        with open(PISHOCK_CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"⚠️ Could not save PiShock config: {e}")
        return False

def trigger_pishock(operation=None, intensity=None, duration=None):
    """Trigger PiShock device"""
    import requests
    
    config = load_pishock_config()
    
    if not config.get('enabled'):
        print("⚠️ PiShock is disabled")
        return False
    
    if not all([config.get('username'), config.get('api_key'), config.get('sharecode')]):
        print("❌ PiShock not configured properly")
        return False
    
    # Use provided values or defaults from config
    op = operation if operation is not None else config.get('operation', 0)
    intensity_val = intensity if intensity is not None else config.get('intensity', 30)
    duration_val = duration if duration is not None else config.get('duration', 1)
    
    # Validate values
    intensity_val = max(0, min(100, intensity_val))  # Clamp 0-100
    duration_val = max(1, min(15, duration_val))  # Clamp 1-15 seconds
    
    payload = {
        'Username': config['username'],
        'Name': config.get('name', 'PiShock'),
        'Code': config['sharecode'],
        'Intensity': str(intensity_val),
        'Duration': str(duration_val),
        'Apikey': config['api_key'],
        'Op': str(op)
    }
    
    try:
        print(f"⚡ Sending PiShock command: op={op}, intensity={intensity_val}, duration={duration_val}")
        response = requests.post(PISHOCK_API_URL, json=payload, timeout=5)
        
        if response.status_code == 200:
            print(f"✅ PiShock triggered successfully")
            return True
        else:
            print(f"❌ PiShock API error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ PiShock request failed: {e}")
        return False

@app.route('/')
def index():
    """Main page with clicker button"""
    return render_template('index.html', 
                         click_count=clicker.click_count,
                         last_click=clicker.last_click_time)

@app.route('/click', methods=['POST'])
def trigger_click():
    """API endpoint to trigger a click"""
    sound_type = request.json.get('sound_type', 'default') if request.is_json else 'default'
    
    # Get user info
    session_id = get_or_create_session_id()
    nickname = request.json.get('nickname') if request.is_json else None
    
    # If nickname provided, update it
    if nickname:
        set_user_nickname(nickname, session_id)
    else:
        nickname = get_user_nickname(session_id)
    
    # Check rate limit
    allowed, wait_time, click_count = check_rate_limit(session_id, nickname)
    
    if not allowed:
        minutes = wait_time // 60
        seconds = wait_time % 60
        
        # Cute rate limit messages
        messages = [
            f"Whoa there, {nickname or 'friend'}! 💜 You've already rewarded the good boy/girl {click_count} times in the past hour. Give them a break!",
            f"Easy now, {nickname or 'cutie'}! 💕 {click_count} clicks in an hour is plenty! They need time to rest!",
            f"Slow down, {nickname or 'sweetheart'}! 🎯 You've clicked {click_count} times already. Let them catch their breath!",
            f"Hold on, {nickname or 'dear'}! ✨ {click_count} rewards in one hour? They're gonna get spoiled!",
        ]
        
        import random
        cute_message = random.choice(messages)
        
        if minutes > 0:
            wait_str = f"{minutes} minute{'s' if minutes != 1 else ''} and {seconds} second{'s' if seconds != 1 else ''}"
        else:
            wait_str = f"{seconds} second{'s' if seconds != 1 else ''}"
        
        return jsonify({
            'success': False,
            'rate_limited': True,
            'message': cute_message,
            'wait_time': wait_time,
            'wait_string': wait_str,
            'clicks_in_window': click_count,
            'max_clicks': MAX_CLICKS_PER_HOUR
        }), 429
    
    # Record this click for rate limiting
    record_click_for_rate_limit(session_id)
    
    # Check if voice message exists BEFORE playing sounds
    voice_message_path = get_voice_message_path()
    voice_message_existed = voice_message_path is not None
    
    # Pre-convert voice message if needed (do this BEFORE playing click sound)
    converted_voice_path = None
    if voice_message_existed and voice_message_path:
        # If it's not a WAV, convert it now while we prepare to play
        if not voice_message_path.endswith('.wav'):
            print(f"🔄 Pre-converting voice message while click sound plays...")
            converted_voice_path = convert_to_wav(voice_message_path)
        else:
            converted_voice_path = voice_message_path
    
    # Play sound and voice message in a separate thread to avoid blocking
    def play_sounds_and_voice():
        # Play click sound first (this gives time for conversion to finish)
        clicker.play_sound(sound_type, session_id, nickname)
        
        # If voice message exists, play it on the server
        if voice_message_existed and (converted_voice_path or voice_message_path):
            try:
                # Much shorter delay since conversion is already done
                time.sleep(0.1)
                
                # Use converted file if available, otherwise try original
                audio_to_play = converted_voice_path if converted_voice_path else voice_message_path
                print(f"🎤 Playing voice message on server: {audio_to_play}")
                
                # Play the audio file
                success = play_audio_file(audio_to_play)
                
                if not success:
                    print(f"⚠️ Could not play voice message. Format may not be supported.")
                    print(f"💡 Tip: Install ffmpeg for automatic conversion support")
                
                # Delete after playing (or after failed attempt)
                print(f"🗑️ Deleting voice message files...")
                delete_all_voice_messages()
                
            except Exception as e:
                print(f"❌ Failed to play voice message: {e}")
                import traceback
                traceback.print_exc()
                # Still try to delete even if playback failed
                try:
                    delete_all_voice_messages()
                except:
                    pass
    
    threading.Thread(target=play_sounds_and_voice).start()
    
    return jsonify({
        'success': True,
        'message': f'Click triggered! Total clicks: {clicker.click_count}',
        'click_count': clicker.click_count,
        'daily_click_count': clicker.daily_click_count,
        'timestamp': time.time(),
        'voice_message_exists': voice_message_existed
    })

@app.route('/bonk', methods=['POST'])
def trigger_bonk():
    """API endpoint to trigger a bonk (sound + optional PiShock)"""
    # Get user info
    session_id = get_or_create_session_id()
    nickname = request.json.get('nickname') if request.is_json else None
    
    # Get optional intensity/duration from hold time
    data = request.json if request.is_json else {}
    intensity = data.get('intensity')  # Optional override
    duration = data.get('duration')    # Optional override
    
    if nickname:
        set_user_nickname(nickname, session_id)
    else:
        nickname = get_user_nickname(session_id)
    
    # Play bonk sound
    def play_bonk():
        try:
            if os.path.exists(BONK_SOUND_FILE):
                pygame.mixer.Sound(BONK_SOUND_FILE).play()
                print(f"💥 BONK sound played by {nickname or 'Anonymous'}")
            else:
                # Fallback bonk sound (two quick beeps)
                import winsound
                winsound.Beep(600, 100)
                time.sleep(0.05)
                winsound.Beep(400, 150)
                print(f"💥 BONK beep played by {nickname or 'Anonymous'}")
        except Exception as e:
            print(f"❌ Bonk sound error: {e}")
    
    threading.Thread(target=play_bonk).start()
    
    # Try to trigger PiShock if enabled (with optional intensity/duration)
    pishock_triggered = False
    pishock_config = load_pishock_config()
    
    if pishock_config.get('enabled'):
        pishock_triggered = trigger_pishock(
            operation=pishock_config.get('operation', 0),
            intensity=intensity,
            duration=duration
        )
        
        if intensity or duration:
            print(f"⚡ Custom bonk: intensity={intensity}, duration={duration}")
    
    return jsonify({
        'success': True,
        'message': 'Bonk triggered!',
        'pishock_triggered': pishock_triggered,
        'intensity': intensity,
        'duration': duration,
        'timestamp': time.time()
    })

@app.route('/zap', methods=['POST'])
def trigger_zap():
    """API endpoint for MAX ZAP - preset strong shock"""
    # Get user info
    session_id = get_or_create_session_id()
    nickname = request.json.get('nickname') if request.is_json else None
    
    if nickname:
        set_user_nickname(nickname, session_id)
    else:
        nickname = get_user_nickname(session_id)
    
    # Get PiShock config for max zap preset
    pishock_config = load_pishock_config()
    
    if not pishock_config.get('enabled'):
        return jsonify({
            'success': False,
            'message': 'PiShock is not enabled',
            'pishock_triggered': False
        }), 400
    
    # Use max zap preset (or allow override from request)
    data = request.json if request.is_json else {}
    max_intensity = data.get('intensity', pishock_config.get('max_zap_intensity', 70))
    max_duration = data.get('duration', pishock_config.get('max_zap_duration', 3))
    
    print(f"⚡⚡⚡ MAX ZAP triggered by {nickname or 'Anonymous'}: {max_intensity}% for {max_duration}s")
    
    # Trigger PiShock with max settings
    pishock_triggered = trigger_pishock(
        operation=pishock_config.get('operation', 0),
        intensity=max_intensity,
        duration=max_duration
    )
    
    return jsonify({
        'success': True,
        'message': 'MAX ZAP triggered!',
        'pishock_triggered': pishock_triggered,
        'intensity': max_intensity,
        'duration': max_duration,
        'timestamp': time.time()
    })

@app.route('/stats')
def get_stats():
    """Get clicker statistics"""
    return jsonify({
        'click_count': clicker.click_count,
        'daily_click_count': clicker.daily_click_count,
        'current_date': clicker.current_date,
        'click_history': clicker.click_history,
        'last_click_time': clicker.last_click_time,
        'sound_file_exists': os.path.exists(SOUND_FILE),
        'sound_file_path': os.path.abspath(SOUND_FILE),
        'vrchat_connected': clicker.vrchat_connected,
        'osc_enabled': osc_client is not None
    })

@app.route('/test')
def test_audio():
    """Test endpoint to verify audio works"""
    threading.Thread(target=clicker.play_sound).start()
    return jsonify({'message': 'Test click triggered!'})

@app.route('/vrchat/click', methods=['POST'])
def vrchat_click():
    """VRChat-specific click endpoint with enhanced parameters"""
    data = request.json if request.is_json else {}
    trigger_type = data.get('type', 'click')
    intensity = data.get('intensity', 1.0)  # 0.0 to 1.0
    
    # Play sound in a separate thread
    threading.Thread(target=clicker.play_sound, args=(trigger_type,)).start()
    
    # Send additional VRChat parameters if specified
    if osc_client and data.get('vrchat_params'):
        try:
            for param, value in data['vrchat_params'].items():
                osc_client.send_message(f"/avatar/parameters/{param}", value)
        except Exception as e:
            print(f"❌ VRChat parameter send failed: {e}")
    
    return jsonify({
        'success': True,
        'message': f'VRChat click triggered! Type: {trigger_type}',
        'click_count': clicker.click_count,
        'timestamp': time.time(),
        'vrchat_connected': clicker.vrchat_connected
    })

@app.route('/vrchat/status')
def vrchat_status():
    """Get VRChat OSC connection status"""
    return jsonify({
        'osc_enabled': osc_client is not None,
        'vrchat_connected': clicker.vrchat_connected,
        'osc_target': f"{VRCHAT_OSC_IP}:{VRCHAT_OSC_PORT}",
        'receive_port': OSC_RECEIVE_PORT
    })

@app.route('/vrchat/test-osc')
def test_osc():
    """Test OSC connection to VRChat"""
    if osc_client:
        try:
            # Send a test parameter
            osc_client.send_message("/avatar/parameters/OSCTest", True)
            threading.Thread(target=lambda: (time.sleep(0.5), osc_client.send_message("/avatar/parameters/OSCTest", False))).start()
            return jsonify({'success': True, 'message': 'OSC test message sent!'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    else:
        return jsonify({'success': False, 'error': 'OSC not initialized'})

@app.route('/tunnel/status')
def tunnel_status():
    """Get tunnel status and public URL"""
    return jsonify({
        'tunnel_active': public_tunnel_url is not None,
        'public_url': public_tunnel_url,
        'ngrok_available': NGROK_AVAILABLE,
        'local_url': request.url_root
    })

@app.route('/tunnel/setup', methods=['POST'])
def setup_tunnel_endpoint():
    """Try to set up a public tunnel"""
    success = setup_tunnel()
    return jsonify({
        'success': success,
        'public_url': public_tunnel_url,
        'message': 'Tunnel setup successful!' if success else 'Tunnel setup failed - check console for details'
    })

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    """Get or update user settings"""
    if request.method == 'POST':
        try:
            settings_data = request.json
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(settings_data, f, indent=2)
            return jsonify({'success': True, 'message': 'Settings saved!'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    else:
        # Load settings
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r') as f:
                    return jsonify(json.load(f))
            else:
                # Default settings (for long distance relationships)
                return jsonify({
                    'title': 'Good Boy!',
                    'subtitle': 'Remote Clicker Training 🎯',
                    'timezones': [
                        {'name': 'Partner 1', 'offset': 0},
                        {'name': 'Partner 2', 'offset': 0}
                    ],
                    'theme': 'purple'
                })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

@app.route('/voice-message', methods=['POST'])
def upload_voice_message():
    """Upload a voice message to play after clicks"""
    try:
        print("📥 Voice message upload request received")
        
        if 'audio' not in request.files:
            print("❌ No audio file in request")
            return jsonify({'success': False, 'error': 'No audio file provided'})
        
        audio_file = request.files['audio']
        filename = audio_file.filename or 'voice_message.webm'
        print(f"📁 Received file: {filename}")
        
        # Extract extension from filename
        ext = os.path.splitext(filename)[1] or '.webm'
        print(f"📝 File extension: {ext}")
        
        # Ensure voice message directory exists
        os.makedirs(VOICE_MESSAGE_DIR, exist_ok=True)
        
        # Delete any existing voice messages first
        delete_all_voice_messages()
        
        # Save with correct extension
        voice_path = os.path.join(VOICE_MESSAGE_DIR, f"{VOICE_MESSAGE_BASE}{ext}")
        print(f"💾 Saving to: {voice_path}")
        
        audio_file.save(voice_path)
        
        file_size = os.path.getsize(voice_path)
        print(f"✅ Voice message uploaded successfully: {filename} ({file_size} bytes)")
        
        return jsonify({
            'success': True, 
            'message': 'Voice message saved!', 
            'size': file_size,
            'filename': f"{VOICE_MESSAGE_BASE}{ext}"
        })
    except Exception as e:
        print(f"❌ Voice message upload failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/voice-message', methods=['GET'])
def get_voice_message():
    """Check if voice message exists"""
    voice_path = get_voice_message_path()
    if voice_path:
        # Return the relative path for the browser
        relative_path = voice_path.replace('\\', '/')
        return jsonify({
            'exists': True,
            'path': f"/{relative_path}"
        })
    return jsonify({
        'exists': False,
        'path': None
    })

@app.route('/voice-message', methods=['DELETE'])
def delete_voice_message():
    """Delete the voice message"""
    try:
        delete_all_voice_messages()
        return jsonify({'success': True, 'message': 'Voice message deleted!'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/user/nickname', methods=['GET', 'POST'])
def user_nickname():
    """Get or set user nickname"""
    session_id = get_or_create_session_id()
    
    if request.method == 'POST':
        try:
            nickname = request.json.get('nickname', '').strip()
            if not nickname or len(nickname) > 20:
                return jsonify({'success': False, 'error': 'Invalid nickname'})
            
            color = set_user_nickname(nickname, session_id)
            return jsonify({
                'success': True, 
                'nickname': nickname,
                'color': color,
                'session_id': session_id
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    else:
        # GET - return current nickname
        nickname = get_user_nickname(session_id)
        sessions = load_sessions()
        color = sessions.get(session_id, {}).get('color', '💜')
        
        return jsonify({
            'nickname': nickname,
            'color': color,
            'session_id': session_id,
            'has_nickname': nickname is not None
        })

@app.route('/admin/users', methods=['GET'])
def get_users():
    """Get list of all users (for admin to assign custom sounds)"""
    sessions = load_sessions()
    users = []
    
    for session_id, data in sessions.items():
        users.append({
            'session_id': session_id,
            'nickname': data.get('nickname', 'Anonymous'),
            'color': data.get('color', '💜'),
            'custom_sound': data.get('custom_sound', None),
            'last_seen': data.get('last_seen', 0)
        })
    
    # Sort by last seen (most recent first)
    users.sort(key=lambda x: x['last_seen'], reverse=True)
    
    return jsonify({'users': users})

@app.route('/admin/user/<session_id>/sound', methods=['POST'])
def set_user_sound(session_id):
    """Set custom sound for a specific user"""
    try:
        sound_filename = request.json.get('sound_filename', '')
        
        if set_custom_sound_for_user(session_id, sound_filename):
            return jsonify({'success': True, 'message': 'Custom sound set!'})
        else:
            return jsonify({'success': False, 'error': 'Sound file not found'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/sounds', methods=['GET'])
def list_sounds():
    """List available sound files"""
    sounds_dir = "static/sounds"
    
    # Create sounds directory if it doesn't exist
    os.makedirs(sounds_dir, exist_ok=True)
    
    sound_files = []
    if os.path.exists(sounds_dir):
        for filename in os.listdir(sounds_dir):
            if filename.endswith(('.wav', '.mp3', '.ogg')):
                sound_files.append({
                    'filename': filename,
                    'path': f"{sounds_dir}/{filename}"
                })
    
    return jsonify({
        'sounds': sound_files,
        'default_sound': SOUND_FILE
    })

@app.route('/admin/rate-limit', methods=['GET', 'POST'])
def manage_rate_limit():
    """Get or update rate limit settings"""
    global MAX_CLICKS_PER_HOUR, RATE_LIMIT_WINDOW
    
    if request.method == 'POST':
        try:
            new_limit = request.json.get('max_clicks_per_hour')
            if new_limit and isinstance(new_limit, int) and new_limit > 0:
                MAX_CLICKS_PER_HOUR = new_limit
                return jsonify({
                    'success': True,
                    'max_clicks_per_hour': MAX_CLICKS_PER_HOUR
                })
            else:
                return jsonify({'success': False, 'error': 'Invalid rate limit'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    else:
        return jsonify({
            'max_clicks_per_hour': MAX_CLICKS_PER_HOUR,
            'window_seconds': RATE_LIMIT_WINDOW
        })

@app.route('/admin/pishock', methods=['GET', 'POST'])
def manage_pishock():
    """Get or update PiShock configuration"""
    if request.method == 'POST':
        try:
            config = request.json
            if save_pishock_config(config):
                return jsonify({'success': True, 'message': 'PiShock config saved!'})
            else:
                return jsonify({'success': False, 'error': 'Failed to save config'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    else:
        return jsonify(load_pishock_config())

@app.route('/admin/pishock/test', methods=['POST'])
def test_pishock():
    """Test PiShock connection"""
    try:
        data = request.json if request.is_json else {}
        operation = data.get('operation', 2)  # Default to beep
        intensity = data.get('intensity', 30)
        duration = data.get('duration', 1)
        
        success = trigger_pishock(operation, intensity, duration)
        
        if success:
            return jsonify({'success': True, 'message': 'PiShock test successful!'})
        else:
            return jsonify({'success': False, 'error': 'PiShock trigger failed'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/sounds/set-default', methods=['POST'])
def set_default_sounds():
    """Set default click and bonk sounds"""
    global SOUND_FILE, BONK_SOUND_FILE
    
    try:
        data = request.json
        click_sound = data.get('click_sound')
        bonk_sound = data.get('bonk_sound')
        
        if click_sound:
            click_path = f"static/sounds/{click_sound}"
            if os.path.exists(click_path):
                SOUND_FILE = click_path
                print(f"🔊 Default click sound set to: {click_sound}")
        
        if bonk_sound:
            bonk_path = f"static/sounds/{bonk_sound}"
            if os.path.exists(bonk_path):
                BONK_SOUND_FILE = bonk_path
                print(f"💥 Default bonk sound set to: {bonk_sound}")
        
        return jsonify({
            'success': True,
            'click_sound': SOUND_FILE,
            'bonk_sound': BONK_SOUND_FILE
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    """Get or post chat messages"""
    if request.method == 'POST':
        try:
            message_text = request.json.get('message', '').strip()
            nickname = request.json.get('nickname', '').strip()
            
            if not message_text or len(message_text) > 100:
                return jsonify({'success': False, 'error': 'Invalid message'})
            
            # Get or create session
            session_id = get_or_create_session_id()
            
            # Update nickname if provided
            if nickname:
                color = set_user_nickname(nickname, session_id)
            else:
                nickname = get_user_nickname(session_id) or 'Anonymous'
                sessions = load_sessions()
                color = sessions.get(session_id, {}).get('color', '💜')
            
            # Load existing messages
            messages = []
            if os.path.exists(CHAT_FILE):
                with open(CHAT_FILE, 'r') as f:
                    data = json.load(f)
                    messages = data.get('messages', [])
            
            # Add new message with user info
            messages.append({
                'message': message_text,
                'timestamp': time.time(),
                'session_id': session_id,
                'nickname': nickname,
                'color': color
            })
            
            # Keep only last 50 messages
            messages = messages[-50:]
            
            # Save messages
            with open(CHAT_FILE, 'w') as f:
                json.dump({'messages': messages}, f, indent=2)
            
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    else:
        # GET - return messages
        try:
            if os.path.exists(CHAT_FILE):
                with open(CHAT_FILE, 'r') as f:
                    data = json.load(f)
                    # Return last 20 messages
                    messages = data.get('messages', [])[-20:]
                    return jsonify({'messages': messages})
            else:
                return jsonify({'messages': []})
        except Exception as e:
            return jsonify({'messages': []})

if __name__ == '__main__':
    print("🎮 Starting Remote Audio Clicker Server with VRChat OSC Support...")
    print(f"📁 Looking for sound file: {os.path.abspath(SOUND_FILE)}")
    
    if not os.path.exists(SOUND_FILE):
        print("⚠️ Custom sound file not found - will use system beep")
        print(f"💡 To use custom audio, place a .wav file at: {os.path.abspath(SOUND_FILE)}")
    
    # Initialize OSC for VRChat
    print("\n� Initializing VRChat OSC...")
    if init_osc():
        print("✅ VRChat OSC ready!")
        print("📋 VRChat Avatar Parameters that will be triggered:")
        print("   • /avatar/parameters/RemoteClick (bool)")
        print("   • /avatar/parameters/ClickCount (int)")
        print("   • /avatar/parameters/ClickTrigger (bool)")
        print("   • /avatar/parameters/SpecialTrigger (bool)")
        print("   • /avatar/parameters/OSCTest (bool)")
    else:
        print("⚠️ VRChat OSC initialization failed - audio-only mode")
    
    print("\n�🌐 Server will be available at:")
    print("   • http://localhost:5000 (web interface)")
    print("   • http://localhost:5000/click (basic API endpoint)")
    print("   • http://localhost:5000/vrchat/click (VRChat-enhanced endpoint)")
    print("   • http://localhost:5000/vrchat/status (VRChat OSC status)")
    print("   • http://localhost:5000/test (test audio)")
    print("   • http://localhost:5000/vrchat/test-osc (test VRChat OSC)")
    
    print("\n📖 VRChat Setup Instructions:")
    print("1. Enable OSC in VRChat Settings > OSC > Enabled")
    print("2. Add these parameters to your avatar:")
    print("   - RemoteClick (Bool) - Main trigger")
    print("   - ClickCount (Int) - Total click counter") 
    print("   - ClickTrigger (Bool) - Standard click trigger")
    print("   - SpecialTrigger (Bool) - Special effect trigger")
    print("3. Use these in your avatar's Animator Controller")
    print("4. Test with: http://localhost:5000/vrchat/test-osc")
    
    # Check if ngrok should be set up (but don't connect yet - server needs to be running first)
    print("\n🌐 Public access configuration:")
    if NGROK_AVAILABLE and NGROK_AUTH_TOKEN.strip():
        print("🔐 Ngrok auth token detected - tunnel will be created after server starts")
        print("💡 The tunnel URL will appear in the console shortly...")
    elif NGROK_AVAILABLE and not NGROK_AUTH_TOKEN.strip():
        print("⚠️ Ngrok is installed but no auth token provided")
        print("💡 To enable public access:")
        print("   1. Sign up at https://ngrok.com (free)")
        print("   2. Copy your auth token from the dashboard")
        print("   3. Paste it into NGROK_AUTH_TOKEN in app.py")
    else:
        print("⚠️ Ngrok not installed - using local network only")
        print("💡 To enable public access, install with: pip install pyngrok")
    
    print("\n🚀 Starting server...")
    
    # Set up ngrok tunnel in a separate thread after Flask starts
    if NGROK_AVAILABLE and NGROK_AUTH_TOKEN.strip():
        def delayed_tunnel_setup():
            time.sleep(2)  # Wait for Flask to start
            print("\n🌐 Setting up ngrok tunnel...")
            tunnel_success = setup_tunnel()
            if tunnel_success and public_tunnel_url:
                print(f"\n🎉 PUBLIC ACCESS READY!")
                print(f"🌍 Share this URL with friends: {public_tunnel_url}")
                print("� No port forwarding needed - works from anywhere!")
            else:
                print("\n❌ Tunnel setup failed - check console for details")
        
        threading.Thread(target=delayed_tunnel_setup, daemon=True).start()
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)