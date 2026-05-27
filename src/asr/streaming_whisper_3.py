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
        self.last_voice_time = time.time()
        
    def process_chunk(self, audio_chunk):
        current_time = time.time()
        
        # --- SILENCE DETECTED ---
        if audio_chunk is None:
            # If buffer has audio AND 1.5 seconds of silence has passed
            if len(self.audio_buffer) > 0 and (current_time - self.last_voice_time) > 1.5:
                
                # AGGRESSIVE PURGE: If the audio chunk is less than 0.5 seconds long, 
                # it is almost certainly a noise blip (like a cough or click). Delete it immediately.
                if len(self.audio_buffer) < 8000:
                    self.audio_buffer = np.array([], dtype=np.float32)
                    return None, None

                # Otherwise, it's long enough to be speech. Ask Whisper to check it.
                segments, info = self.model.transcribe(
                    self.audio_buffer, 
                    language="en",
                    initial_prompt=Config.MEDICAL_PROMPT,
                    beam_size=5,
                    condition_on_previous_text=False, 
                    no_speech_threshold=0.6,          
                    log_prob_threshold=-1.0           
                )
                final_text = " ".join([segment.text for segment in segments]).strip()
                
                # CRITICAL: Always empty the bucket after a silence timeout, 
                # even if Whisper found no valid words, to prevent noise buildup.
                self.audio_buffer = np.array([], dtype=np.float32) 
                
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
                log_prob_threshold=-1.0
            )
            current_text = " ".join([segment.text for segment in segments]).strip()
            
            # Safety fallback: Cut off non-stop rambling after 15 seconds
            if len(self.audio_buffer) > 16000 * 15: 
                final_text = current_text
                self.audio_buffer = np.array([], dtype=np.float32)
                return final_text, current_text 
            
            return None, current_text 
            
        return None, None
