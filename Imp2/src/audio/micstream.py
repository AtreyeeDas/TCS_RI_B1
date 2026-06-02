import pyaudio
import numpy as np
import torch
import time
from src.config import Config

class MicStream:
    def __init__(self):
        self.pa = pyaudio.PyAudio()
        print("[Audio] Loading Silero VAD from local disk...")
        self.vad_model, utils = torch.hub.load(
            repo_or_dir=Config.SILERO_VAD_PATH,
            model='silero_vad',
            source='local',
            onnx=False
        )
        self.vad_model.eval()
        self.get_speech_timestamps = utils[0]
        
        self.stream = None
        self.audio_buffer = []
        self.last_voice_time = time.time()
        self.is_recording = False
        
    def start_stream(self):
        self.audio_buffer = []
        self.is_recording = False
        self.stream = self.pa.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=Config.SAMPLE_RATE,
            input=True,
            input_device_index=Config.INPUT_DEVICE_INDEX,
            frames_per_buffer=Config.CHUNK_SIZE
        )
        print("[Audio] Microphone stream ACTIVE (Walkie-Talkie: ON).")

    def stop_stream(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        print("[Audio] Microphone stream PAUSED (Walkie-Talkie: OFF).")

    def get_audio_chunk(self):
        if not self.stream or not self.stream.is_active():
            return None

        try:
            data = self.stream.read(Config.CHUNK_SIZE, exception_on_overflow=False)
            audio_chunk = np.frombuffer(data, dtype=np.float32)
            
            # VAD Inference
            audio_tensor = torch.from_numpy(audio_chunk)
            speech_prob = self.vad_model(audio_tensor, Config.SAMPLE_RATE).item()
            
            if speech_prob > 0.5:
                if not self.is_recording:
                    self.is_recording = True
                self.last_voice_time = time.time()
                self.audio_buffer.append(audio_chunk)
                print(".", end="", flush=True)
            elif self.is_recording:
                self.audio_buffer.append(audio_chunk)
                
                # Check for silence threshold (1.5 seconds)
                if time.time() - self.last_voice_time > Config.SILENCE_THRESHOLD:
                    self.is_recording = False
                    final_audio = np.concatenate(self.audio_buffer)
                    self.audio_buffer = [] # Reset
                    
                    # Aggressive Purge Bug-Fix
                    if len(final_audio) < Config.GHOST_NOISE_THRESHOLD:
                        print("\n[Audio] Ghost noise detected & purged.")
                        return None
                        
                    return final_audio
                    
        except IOError:
            pass
            
        return None
