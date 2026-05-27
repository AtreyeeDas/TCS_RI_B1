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
        self.last_voice_time = time.time() # Tracks when you last made a sound
        
    def process_chunk(self, audio_chunk):
        current_time = time.time()
        
        # --- PHASE 1: SILENCE DETECTION & HANDOFF ---
        if audio_chunk is None:
            # If we have audio AND the user paused for 1.5 seconds...
            if len(self.audio_buffer) > 0 and (current_time - self.last_voice_time) > 1.5:
                
                # Prevent micro-noise hallucinations (ignore anything under 0.5 seconds)
                if len(self.audio_buffer) > 16000 * 0.5:
                    segments, info = self.model.transcribe(
                        self.audio_buffer, 
                        language="en",
                        initial_prompt=Config.MEDICAL_PROMPT,
                        condition_on_previous_text=False, # <--- KILLS THE REPEATING LOOP
                        beam_size=5,
                        temperature=[0.0, 0.2, 0.4]
                    )
                    
                    # KILLS "THANK YOU FOR WATCHING" GHOSTS
                    # Only accept text if the model is confident it's actual speech
                    if info.no_speech_prob < 0.6:
                        final_text = " ".join([segment.text for segment in segments]).strip()
                        
                        # One last safety net against empty or pure hallucination strings
                        if len(final_text) > 3 and "Thank you for watching" not in final_text:
                            self.audio_buffer = np.array([], dtype=np.float32)
                            return final_text, None 
                
                # If it was just a breath or fan noise, clear the buffer quietly
                self.audio_buffer = np.array([], dtype=np.float32)
                return None, None
                
            # Still waiting for either more voice or the 1.5s timeout
            return None, None
            
        # --- PHASE 2: CONTINUOUS LISTENING ---
        # Update the timer because you are currently speaking
        self.last_voice_time = current_time 
        self.audio_buffer = np.concatenate((self.audio_buffer, audio_chunk))
        
        # Generate the live visual partial transcript (if we have at least 1 second of audio)
        if len(self.audio_buffer) >= 16000:
            segments, info = self.model.transcribe(
                self.audio_buffer, 
                language="en",
                initial_prompt=Config.MEDICAL_PROMPT,
                condition_on_previous_text=False, 
                beam_size=1 # Beam size 1 is faster for real-time live typing on the screen
            )
            
            # Only show partials if it's actual speech
            if info.no_speech_prob < 0.6:
                current_text = " ".join([segment.text for segment in segments]).strip()
                return None, current_text 
            
        return None, None
