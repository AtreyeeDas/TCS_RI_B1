import pyaudio
import numpy as np
import queue
import librosa
import torch

class MicStream:
    def __init__(self, target_sample_rate, target_chunk_size, input_device_index=7):
        self.target_sample_rate = target_sample_rate # Whisper expects 16000
        self.pa = pyaudio.PyAudio()
        self.input_device_index = input_device_index # Provide the index from check_mic.py here
        
        # 1. Connect to the specific hardware mic
        try:
            if self.input_device_index is not None:
                device_info = self.pa.get_device_info_by_index(self.input_device_index)
            else:
                device_info = self.pa.get_default_input_device_info()
            self.device_sample_rate = int(device_info['defaultSampleRate'])
            print(f"[Audio] Successfully bound to: {device_info['name']}")
        except IOError as e:
            print(f"[Audio Error] Could not find microphone: {e}")
            self.device_sample_rate = 48000 
            
        # 2. Silero VAD strictly prefers 512 frames (32ms) at 16kHz
        # Calculate how many frames we need to capture at the hardware's native rate to equal 32ms
        self.device_chunk_size = int(self.device_sample_rate * (512 / 16000.0))
        
        # 3. Load Silero VAD Offline
        print("[Audio] Loading Silero VAD from local disk...")
        self.vad_model, _ = torch.hub.load(
            repo_or_dir='./offline_models/silero-vad-master',
            model='silero_vad',
            source='local',
            onnx=False
        )
        self.vad_model.eval() # Set to evaluation mode

        self.stream = None
        self.audio_queue = queue.Queue()

    def start(self):
        self.stream = self.pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.device_sample_rate,
            input=True,
            input_device_index=self.input_device_index,
            frames_per_buffer=self.device_chunk_size,
            stream_callback=self._callback
        )
        self.stream.start_stream()
        print("[Audio] Microphone stream started.")

    def _callback(self, in_data, frame_count, time_info, status):
        # 4. Convert incoming bytes to float32
        audio_float = np.frombuffer(in_data, dtype=np.int16).astype(np.float32) / 32768.0

        # 5. Downsample to 16kHz for Silero and Whisper
        if self.device_sample_rate != self.target_sample_rate:
            resampled_float = librosa.resample(
                audio_float, 
                orig_sr=self.device_sample_rate, 
                target_sr=self.target_sample_rate
            )
        else:
            resampled_float = audio_float

        # 6. Ensure exactly 512 samples for Silero
        if len(resampled_float) > 512:
            resampled_float = resampled_float[:512]
        elif len(resampled_float) < 512:
            resampled_float = np.pad(resampled_float, (0, 512 - len(resampled_float)))

        # 7. Run Silero VAD Inference
        with torch.no_grad():
            audio_tensor = torch.from_numpy(resampled_float)
            speech_prob = self.vad_model(audio_tensor, self.target_sample_rate).item()

        # 8. Push to pipeline if confidence is high (> 0.5)
        if speech_prob > 0.5:
            resampled_int16 = (resampled_float * 32768.0).astype(np.int16)
            self.audio_queue.put(resampled_int16.tobytes())
            print(".", end="", flush=True) # Print a dot to visually confirm voice detection!
            
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
        print("\n[Audio] Microphone stream stopped.")
