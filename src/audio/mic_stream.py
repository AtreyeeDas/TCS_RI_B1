import pyaudio
import webrtcvad
import numpy as np
import queue

class MicStream:
    def __init__(self, sample_rate, chunk_size):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.pa = pyaudio.PyAudio()
        self.vad = webrtcvad.Vad(3) # Aggressiveness 0-3
        self.stream = None
        self.audio_queue = queue.Queue()

    def start(self):
        self.stream = self.pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            stream_callback=self._callback
        )
        self.stream.start_stream()
        print("[Audio] Microphone stream started.")

    def _callback(self, in_data, frame_count, time_info, status):
        is_speech = self.vad.is_speech(in_data, self.sample_rate)
        if is_speech:
            self.audio_queue.put(in_data)
        return (in_data, pyaudio.paContinue)

    def get_audio_chunk(self):
        chunks = []
        while not self.audio_queue.empty():
            chunks.append(self.audio_queue.get())
        if chunks:
            # Combine bytes and convert to float32 numpy array for Whisper
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
