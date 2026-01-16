from flask import Flask, render_template, jsonify, request
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

app = Flask(__name__)

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

# VRChat OSC Configuration
VRCHAT_OSC_IP = "127.0.0.1"
VRCHAT_OSC_PORT = 9000
OSC_RECEIVE_PORT = 9001

# Ngrok Configuration - ADD YOUR TOKEN HERE!
NGROK_AUTH_TOKEN = "37RmfMJz7JxXshckxhaoI6frogq_554P22JoSxWnNbQBAj7bh"  # Paste your ngrok token between the quotes
# Get your token from: https://dashboard.ngrok.com/get-started/your-authtoken

# OSC Client for sending to VRChat
osc_client = None

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
        self.last_click_time = None
        self.vrchat_connected = False
        
    def play_sound(self, sound_type="default"):
        """Play different types of sounds"""
        try:
            if os.path.exists(SOUND_FILE):
                # Play custom sound file
                pygame.mixer.Sound(SOUND_FILE).play()
                print(f"🎵 Playing custom sound: {SOUND_FILE}")
            else:
                # Fall back to system beep
                import winsound
                winsound.Beep(800, 200)  # frequency, duration
                print("🔊 Playing system beep")
                
            self.click_count += 1
            self.last_click_time = time.time()
            print(f"🖱️ Click #{self.click_count} triggered!")
            
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
    
    # Play sound in a separate thread to avoid blocking
    threading.Thread(target=clicker.play_sound, args=(sound_type,)).start()
    
    return jsonify({
        'success': True,
        'message': f'Click triggered! Total clicks: {clicker.click_count}',
        'click_count': clicker.click_count,
        'timestamp': time.time()
    })

@app.route('/stats')
def get_stats():
    """Get clicker statistics"""
    return jsonify({
        'click_count': clicker.click_count,
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
    
    print("\n🚀 Starting server...")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)