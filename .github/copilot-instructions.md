<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Remote Audio Clicker Project

This is a Python Flask web application that allows friends to remotely trigger audio sounds on your computer through web buttons and API calls.

## Project Features
- Web interface with clickable button to trigger audio
- REST API endpoints for remote triggering via HTTP requests  
- Audio playback using pygame mixer
- Click statistics and tracking
- Cross-platform audio support (custom sounds + system beep fallback)

## Development Guidelines
- Use Flask for web server functionality
- Implement audio playback with pygame
- Create responsive web interface with HTML/CSS/JavaScript
- Support both custom audio files and system beep fallback
- Provide API endpoints for programmatic access
- Include proper error handling and logging

## Project Structure
- `app.py` - Main Flask application
- `templates/` - HTML templates for web interface
- `static/` - CSS, JS, and audio assets
- `requirements.txt` - Python dependencies
- `README.md` - Project documentation

## Audio Requirements
- Support .wav audio files
- Fallback to system beep if custom audio unavailable
- Thread-safe audio playback to prevent blocking
- Multiple sound type support for different trigger types