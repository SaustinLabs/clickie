#!/usr/bin/env python3
"""
Quick script to generate a bonk.wav sound effect
Uses pygame and struct to create a comedic bonk sound
"""

import pygame
import struct
import math
import os

def generate_bonk_sound(filename='static/bonk.wav', duration=0.4, sample_rate=44100):
    """
    Generate a comedic bonk sound effect using pygame
    - Quick attack with high frequency
    - Rapid decay to lower frequency
    - Short duration for punchy effect
    """
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Initialize pygame mixer
    pygame.mixer.init(frequency=sample_rate, size=-16, channels=1)
    
    # Generate samples
    samples = []
    num_samples = int(sample_rate * duration)
    
    for i in range(num_samples):
        t = i / sample_rate
        
        # Frequency sweep from high to low (bonk character)
        start_freq = 1200
        end_freq = 180
        freq = start_freq + (end_freq - start_freq) * (t / duration)
        
        # Main tone
        tone = math.sin(2 * math.pi * freq * t)
        
        # Add harmonics for richness
        tone += 0.3 * math.sin(4 * math.pi * freq * t)
        tone += 0.15 * math.sin(6 * math.pi * freq * t)
        
        # Exponential decay envelope (quick attack, fast decay)
        envelope = math.exp(-9 * t)
        
        # Combine and normalize
        sample = tone * envelope * 0.7
        
        # Convert to 16-bit integer
        sample_int = int(sample * 32767)
        sample_int = max(-32768, min(32767, sample_int))
        samples.append(sample_int)
    
    # Create sound buffer
    sound_buffer = struct.pack('<%dh' % len(samples), *samples)
    
    # Create pygame Sound object and save to file
    sound = pygame.mixer.Sound(buffer=sound_buffer)
    
    # Save using pygame's built-in export
    # Note: pygame doesn't have direct .wav export, so we'll use a workaround
    # We'll create a simple WAV file manually
    write_wav_file(filename, samples, sample_rate)
    
    print(f"✅ Generated bonk sound: {filename}")
    print(f"   Duration: {duration}s, Sample rate: {sample_rate}Hz")

def write_wav_file(filename, samples, sample_rate):
    """Write a simple WAV file manually"""
    import wave
    
    with wave.open(filename, 'w') as wav_file:
        # Set parameters: 1 channel, 2 bytes per sample, sample rate
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        # Write samples
        sound_buffer = struct.pack('<%dh' % len(samples), *samples)
        wav_file.writeframes(sound_buffer)

if __name__ == '__main__':
    try:
        generate_bonk_sound()
        print("\n💥 Bonk sound ready! You can test it with the bonk button.")
    except Exception as e:
        print(f"❌ Error generating bonk sound: {e}")
        import traceback
        traceback.print_exc()

