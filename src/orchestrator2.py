from src.config import Config
from src.audio.mic_stream import MicStream
from src.asr.streaming_whisper import StreamingWhisper
from src.llm.qwen_engine import QwenEngine
# 1. Update the import to your new engine
from src.tts.xtts_engine import MultilingualTTSEngine 
import time

class PipelineOrchestrator:
    def __init__(self):
        Config.setup_dirs()
        self.mic = MicStream(Config.SAMPLE_RATE, Config.CHUNK_SIZE, input_device_index=7)
        self.asr = StreamingWhisper(Config.WHISPER_MODEL, Config.DEVICE, Config.COMPUTE_TYPE)
        self.llm = QwenEngine(Config.LLM_MODEL)
        
        # 2. Initialize XTTS
        # Make sure the path matches where you downloaded the Coqui model
        self.tts = MultilingualTTSEngine("./offline_models/xtts-v2", Config.TTS_OUTPUT_DIR)

    def detect_language(self, text):
        """Checks if text contains Devanagari characters for Hindi routing."""
        for char in text:
            if '\u0900' <= char <= '\u097F':
                return "hi"
        return "en"

    def run(self):
        self.mic.start()
        print("\n=== Pipeline Active. Start speaking. Press Ctrl+C to stop. ===")
        
        try:
            while True:
                time.sleep(0.01) 
                chunk = self.mic.get_audio_chunk()
                final_text, partial_text = self.asr.process_chunk(chunk)
                
                if partial_text:
                    print(f"\r[ASR Partial]: {partial_text[:80].ljust(80)}", end="", flush=True)

                if final_text:
                    print(f"\n[ASR Final]: {final_text}")
                    
                    # Pause mic so PyAudio doesn't overflow and it doesn't hear itself speaking
                    self.mic.pause_listening() 
                    
                    print("[LLM] Generating response...")
                    llm_response = self.llm.generate_response(final_text)
                    print(f"[LLM Output]: {llm_response}")
                    
                    # 3. Detect Language & Speak!
                    target_lang = self.detect_language(llm_response)
                    self.tts.synthesize_and_play(llm_response, language=target_lang)
                    
                    self.mic.resume_listening()
                    print("\n=== Ready for your next sentence. ===")
                    
        except KeyboardInterrupt:
            print("\nShutting down pipeline...")
            self.mic.stop()
