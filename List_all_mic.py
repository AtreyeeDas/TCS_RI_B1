import pyaudio

p = pyaudio.PyAudio()
print("\n--- Available Input Devices (Microphones) ---")
found_mic = False

for i in range(p.get_device_count()):
    dev_info = p.get_device_info_by_index(i)
    # Only show devices that can actually record audio
    if dev_info.get('maxInputChannels') > 0:
        print(f"Index {i}: {dev_info.get('name')}")
        found_mic = True

if not found_mic:
    print("❌ PyAudio still cannot see ANY microphones.")
else:
    print("\n✅ Microphones found! Look for your 'Airdopes' or 'pulse' / 'default' in the list above.")

p.terminate()
