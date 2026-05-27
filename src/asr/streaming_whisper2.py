import time
from faster_whisper import WhisperModel
import numpy as np
from src.config import Config

class StreamingWhisper:
    def __init__(self, model_path, device, compute_type):
        print(f"[ASR] Loading Faster-Whisper from local path: {model_path} ...")
        self.model = WhisperModel(
            model_size_or_path=model_path, 
            device=device, 
            compute_type=compute_type,
            local_files_only=True
        )
        self.audio_buffer = np.array([], dtype=np.float32)
        self.last_voice_time = time.time() # Timer for silence detection
        
    def process_chunk(self, audio_chunk):
        current_time = time.time()
        
        # --- SILENCE ENDPOINTING ---
        if audio_chunk is None:
            # If buffer has audio AND 1.5 seconds of silence has passed -> FLUSH to LLM
            if len(self.audio_buffer) > 0 and (current_time - self.last_voice_time) > 1.5:
                segments, info = self.model.transcribe(
                    self.audio_buffer, 
                    language="en",
                    initial_prompt=Config.MEDICAL_PROMPT,
                    beam_size=5,
                    condition_on_previous_text=False, # Kills the repeating loop bug
                    no_speech_threshold=0.6,          # Ignores pure background noise
                    logprob_threshold=-1.0            # Rejects low-confidence hallucinations
                )
                final_text = " ".join([segment.text for segment in segments]).strip()
                
                # Clear the buffer
                self.audio_buffer = np.array([], dtype=np.float32) 
                
                # Only return if the text isn't empty
                if final_text:
                    return final_text, None 
            
            return None, None
            
        # --- VOICE DETECTED ---
        self.last_voice_time = current_time 
        self.audio_buffer = np.concatenate((self.audio_buffer, audio_chunk))
        
        # Process partials once we have at least 1 second of audio
        if len(self.audio_buffer) >= 16000:
            segments, info = self.model.transcribe(
                self.audio_buffer, 
                language="en",
                initial_prompt=Config.MEDICAL_PROMPT,
                beam_size=5,                          
                condition_on_previous_text=False,
                no_speech_threshold=0.6,
                logprob_threshold=-1.0
            )
            current_text = " ".join([segment.text for segment in segments]).strip()
            
            # Safety fallback: If someone talks non-stop for 15 seconds, force a cut
            if len(self.audio_buffer) > 16000 * 15: 
                final_text = current_text
                self.audio_buffer = np.array([], dtype=np.float32)
                return final_text, current_text 
            
            return None, current_text 
            
        return None, None
