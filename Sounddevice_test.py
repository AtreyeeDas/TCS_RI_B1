import sounddevice as sd
import numpy as np

print("--- Available Audio Devices ---")
print(sd.query_devices())
print("\n--- Testing Default Mic ---")
print("Speak into your Airdopes for 3 seconds...")

try:
    # Record 3 seconds of audio at 16kHz
    recording = sd.rec(int(3 * 16000), samplerate=16000, channels=1, dtype='int16')
    sd.wait() # Wait until recording is finished
    
    # Check if the array actually caught varying sound waves (not just dead silence)
    if np.max(np.abs(recording)) > 0:
        print("✅ SUCCESS! sounddevice heard you perfectly through the Bluetooth headset.")
    else:
        print("⚠️ Warning: Connected, but recorded dead silence (Check if Airdopes are muted).")
except Exception as e:
    print(f"❌ Error: {e}")
