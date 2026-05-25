from faster_whisper import WhisperModel
import numpy as np

class StreamingWhisper:
    def __init__(self, model_size, device, compute_type):
        print(f"[ASR] Loading Faster-Whisper ({model_size})...")
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        self.audio_buffer = np.array([], dtype=np.float32)
        self.last_stabilized_text = ""
        
    def process_chunk(self, audio_chunk):
        if audio_chunk is None:
            return None, None
            
        self.audio_buffer = np.concatenate((self.audio_buffer, audio_chunk))
        
        # Process if buffer has at least 1 second of audio
        if len(self.audio_buffer) >= 16000:
            segments, info = self.model.transcribe(
                self.audio_buffer, 
                language="en", # Change to "hi" for Hindi
                condition_on_previous_text=False
            )
            
            current_text = " ".join([segment.text for segment in segments]).strip()
            
            # Basic Stabilization Logic (Pseudo-streaming)
            # If length exceeds a threshold, consider it stabilized and clear buffer
            if len(self.audio_buffer) > 16000 * 5: # 5 seconds max window
                final_text = current_text
                self.audio_buffer = np.array([], dtype=np.float32)
                return final_text, current_text # final, partial
            
            return None, current_text # None, partial
            
        return None, None
