import re
import logging
from src.tts.xtts_engine import XttsEngine  # Your existing, heavily patched engine

# Optional: Import StyleTTS2 if installed. We use a try-except block so the pipeline
# doesn't crash if you are still setting up the complex StyleTTS2 environment.
try:
    from src.tts.styletts2_engine import StyleTTSEngine
    STYLE_TTS_AVAILABLE = True
except ImportError:
    STYLE_TTS_AVAILABLE = False
    logging.warning("StyleTTS2 not found. Falling back to XTTS for English temporarily.")

class DynamicTTSRouter:
    def __init__(self, xtts_config_path, style_tts_config_path=None):
        """
        Initializes the TTS Router without breaking Phase 1 architectures.
        """
        logging.info("Initializing Dynamic TTS Router...")
        
        # 1. Initialize your existing heavily patched XTTS Engine (Handles Hindi/Hinglish)
        # Your Blackwell sm_120 sinc_resample workaround is preserved inside this class.
        self.xtts_engine = XttsEngine(config_path=xtts_config_path)
        
        # 2. Initialize StyleTTS2 for English (if available)
        if STYLE_TTS_AVAILABLE:
            self.style_tts_engine = StyleTTSEngine(config_path=style_tts_config_path)
        else:
            self.style_tts_engine = None

    def stream_synthesis(self, response_text: str, language_tag: str):
        """
        Splits text into sentences and routes them to the correct TTS engine dynamically.
        """
        # Split by English punctuation (., ?, !) OR Hindi Purna Viram (।)
        # This prevents the TTS from trying to synthesize massive blocks of text at once.
        sentences = re.split(r'(?<=[.?!।])\s+', response_text.strip())
        
        for sentence in sentences:
            if not sentence.strip():
                continue
                
            logging.info(f"Synthesizing [{language_tag}]: {sentence}")
            
            # ROUTING LOGIC
            if language_tag.lower() == "en" and self.style_tts_engine:
                # Route pure English to highly expressive StyleTTS2
                self.style_tts_engine.synthesize_and_play(sentence)
                
            elif language_tag.lower() in ["hi", "hinglish", "en"]:
                # Route Hindi/Hinglish (or English fallback) to XTTS
                # Currently using your 1 cloned audio, ready for the empathetic Hindi audio swap later.
                self.xtts_engine.synthesize_and_play(sentence)
                
            else:
                # Safety fallback
                self.xtts_engine.synthesize_and_play(sentence)

    def update_xtts_reference_audio(self, new_audio_path: str):
        """
        Helper function for Phase 2: Allows dynamic switching of the Hindi clone voice
        (e.g., swapping to 'empathetic_hindi_doctor.wav') on the fly.
        """
        # Re-triggering the CPU-first loading sequence built into your XttsEngine
        logging.info(f"Updating XTTS reference voice to: {new_audio_path}")
        self.xtts_engine.update_speaker_embedding(new_audio_path)
