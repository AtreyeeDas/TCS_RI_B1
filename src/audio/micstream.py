import pyaudio
import webrtcvad
import numpy as np
import queue
import librosa # Using librosa for real-time downsampling

class MicStream:
    def __init__(self, target_sample_rate, target_chunk_size):
        self.target_sample_rate = target_sample_rate # Whisper expects 16000
        self.pa = pyaudio.PyAudio()
        
        # 1. Ask the hardware what sample rate it naturally prefers
        try:
            device_info = self.pa.get_default_input_device_info()
            self.device_sample_rate = int(device_info['defaultSampleRate'])
        except IOError:
            self.device_sample_rate = 48000 # Safe fallback
            
        print(f"[Audio] Hardware mic rate detected: {self.device_sample_rate} Hz. Resampling to {self.target_sample_rate} Hz.")
        
        # 2. Calculate chunk size based on the device's native rate to grab exactly 30ms
        self.device_chunk_size = int(self.device_sample_rate * 0.03)
        
        self.vad = webrtcvad.Vad(3) # Aggressiveness 0-3
        self.stream = None
        self.audio_queue = queue.Queue()

    def start(self):
        self.stream = self.pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.device_sample_rate,
            input=True,
            frames_per_buffer=self.device_chunk_size,
            stream_callback=self._callback
        )
        self.stream.start_stream()
        print("[Audio] Microphone stream started.")

    def _callback(self, in_data, frame_count, time_info, status):
        # 3. Downsample on the fly if the mic isn't exactly 16kHz
        if self.device_sample_rate != self.target_sample_rate:
            audio_float = np.frombuffer(in_data, dtype=np.int16).astype(np.float32) / 32768.0
            resampled_float = librosa.resample(
                audio_float, 
                orig_sr=self.device_sample_rate, 
                target_sr=self.target_sample_rate
            )
            resampled_int16 = (resampled_float * 32768.0).astype(np.int16)
            processed_bytes = resampled_int16.tobytes()
        else:
            processed_bytes = in_data

        # 4. Enforce exact byte length for WebRTC VAD (960 bytes = exactly 30ms at 16kHz)
        if len(processed_bytes) != 960:
            processed_bytes = processed_bytes.ljust(960, b'\0')[:960]

        is_speech = self.vad.is_speech(processed_bytes, self.target_sample_rate)
        if is_speech:
            self.audio_queue.put(processed_bytes)
            
        return (in_data, pyaudio.paContinue)

    def get_audio_chunk(self):
        chunks = []
        while not self.audio_queue.empty():
            chunks.append(self.audio_queue.get())
        if chunks:
            raw_data = b''.join(chunks)
            audio_np = np.frombuffer(raw_data, dtype=np.int16).astype(np.float32) / 32768.0
            return audio_np
        return None

    def stop(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.pa.terminate()
        print("[Audio] Microphone stream stopped.")
