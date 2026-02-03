#!/usr/bin/env python3
"""
Generate simple WAV sound files for chess game
"""

import wave
import struct
import math

def generate_tone(filename, frequency, duration, volume=0.5):
    """Generate a simple tone WAV file"""
    sample_rate = 44100
    num_samples = int(sample_rate * duration)
    
    # Generate samples
    samples = []
    for i in range(num_samples):
        # Simple sine wave with envelope to avoid clicks
        t = i / sample_rate
        envelope = min(1.0, min(t * 50, (duration - t) * 50))  # Fade in/out
        value = volume * envelope * math.sin(2 * math.pi * frequency * t)
        samples.append(int(value * 32767))
    
    # Write WAV file
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        
        for sample in samples:
            wav_file.writeframes(struct.pack('h', sample))

def generate_click(filename, volume=0.3):
    """Generate a click sound (for piece moves)"""
    sample_rate = 44100
    duration = 0.05
    num_samples = int(sample_rate * duration)
    
    samples = []
    for i in range(num_samples):
        t = i / sample_rate
        # Sharp attack, fast decay
        envelope = math.exp(-t * 50)
        # Mix of frequencies for wood-like sound
        value = envelope * (
            0.5 * math.sin(2 * math.pi * 200 * t) +
            0.3 * math.sin(2 * math.pi * 300 * t) +
            0.2 * math.sin(2 * math.pi * 150 * t)
        )
        samples.append(int(value * volume * 32767))
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        for sample in samples:
            wav_file.writeframes(struct.pack('h', sample))

def generate_capture(filename, volume=0.4):
    """Generate a capture sound (slightly different from move)"""
    sample_rate = 44100
    duration = 0.08
    num_samples = int(sample_rate * duration)
    
    samples = []
    for i in range(num_samples):
        t = i / sample_rate
        # Sharper, more percussive
        envelope = math.exp(-t * 40)
        value = envelope * (
            0.6 * math.sin(2 * math.pi * 250 * t) +
            0.4 * math.sin(2 * math.pi * 180 * t)
        )
        samples.append(int(value * volume * 32767))
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        for sample in samples:
            wav_file.writeframes(struct.pack('h', sample))

def main():
    """Generate all sound files"""
    print("Generating sound effects...")
    
    # Move sound - soft click
    print("  - move.wav")
    generate_click('sounds/move.wav', volume=0.25)
    
    # Capture sound - sharper click
    print("  - capture.wav")
    generate_capture('sounds/capture.wav', volume=0.35)
    
    # Check sound - warning tone
    print("  - check.wav")
    generate_tone('sounds/check.wav', frequency=800, duration=0.15, volume=0.3)
    
    # Checkmate sound - victory tone
    print("  - checkmate.wav")
    generate_tone('sounds/checkmate.wav', frequency=600, duration=0.3, volume=0.35)
    
    print("Sound effects generated successfully!")

if __name__ == '__main__':
    main()
