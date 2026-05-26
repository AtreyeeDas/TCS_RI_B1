# check_mic.py
import pyaudio

p = pyaudio.PyAudio()
print("\n--- Available Microphones ---")
for i in range(p.get_device_count()):
    dev = p.get_device_info_by_index(i)
    if dev.get('maxInputChannels') > 0:
        print(f"Index {i}: {dev.get('name')} (Channels: {dev.get('maxInputChannels')}, Native Rate: {int(dev.get('defaultSampleRate'))}Hz)")
print("-----------------------------\n")
p.terminate()
