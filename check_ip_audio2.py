import pyaudio

def check_defaults():
    p = pyaudio.PyAudio()
    
    try:
        default_in = p.get_default_input_device_info()
        print(f"✅ Default Input: {default_in['name']} (Channels: {default_in['maxInputChannels']})")
    except OSError:
        print("❌ No default input device found by PyAudio.")

    try:
        default_out = p.get_default_output_device_info()
        print(f"✅ Default Output: {default_out['name']}")
    except OSError:
        print("❌ No default output device found by PyAudio.")
        
    p.terminate()

if __name__ == "__main__":
    check_defaults()
