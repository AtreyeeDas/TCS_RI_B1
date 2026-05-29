import pyaudio

print("--- Audio Hardware Interrogator ---")
p = pyaudio.PyAudio()
info = p.get_default_output_device_info()

print(f"\nDefault Output Device: {info['name']}")
print(f"Native Hardware Rate: {int(info['defaultSampleRate'])} Hz")

# Test standard formats
test_rates = [8000, 16000, 22050, 24000, 32000, 44100, 48000]
supported_rates = []

print("\nProbing supported playback rates (ignore ALSA warnings)...")
for rate in test_rates:
    try:
        if p.is_format_supported(rate=rate, 
                                 output_device=info['index'], 
                                 output_channels=1, 
                                 output_format=pyaudio.paInt16):
            supported_rates.append(rate)
    except ValueError:
        pass

print(f"\n✅ VERDICT: Your hardware supports these playback rates: {supported_rates}")
p.terminate()
