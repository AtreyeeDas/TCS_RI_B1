from src.config import Config
from src.audio.mic_stream import MicStream
from src.asr.streaming_whisper import StreamingWhisper
from src.llm.qwen_engine import QwenEngine
from src.tts.xtts_engine import MultilingualTTSEngine
import time

class PipelineOrchestrator:
    def __init__(self):
        Config.setup_dirs()
        self.mic = MicStream(Config.SAMPLE_RATE, Config.CHUNK_SIZE, input_device_index=7)
        self.asr = StreamingWhisper(Config.WHISPER_MODEL, Config.DEVICE, Config.COMPUTE_TYPE)
        self.llm = QwenEngine(Config.LLM_MODEL)
        self.tts = MultilingualTTSEngine(Config.TTS_MODEL_PATH, Config.TTS_OUTPUT_DIR)

    def run(self):
        self.mic.start()
        print("\n=== Pipeline Active. Start speaking. Press Ctrl+C to stop. ===")
        
        try:
            while True:
                time.sleep(0.01)
                chunk = self.mic.get_audio_chunk()
                
                # Unpack the new language identifier tracked by Whisper
                final_text, partial_text, detected_lang = self.asr.process_chunk(chunk)
                
                if partial_text:
                    print(f"\r[ASR Partial]: {partial_text[:80].ljust(80)}", end="", flush=True)
                    
                if final_text:
                    # Fallback default if token validation yields None
                    if not detected_lang:
                        detected_lang = "en"
                        
                    print(f"\n[ASR Final ({detected_lang})]: {final_text}")
                    
                    # 1. Pause mic so PyAudio doesn't overflow and it doesn't hear itself speaking
                    self.mic.pause_listening()
                    
                    # 2. AI generation with dynamic language flag ingestion
                    print("[LLM] Generating response...")
                    llm_response = self.llm.generate_response(final_text, detected_language=detected_lang)
                    print(f"[LLM Output]: {llm_response}")
                    
                    # 3. Synchronized language routing directly to XTTS-v2 sentence chunker
                    self.tts.synthesize_and_play(llm_response, language=detected_lang)
                    
                    # 4. Wake mic up for next turn
                    self.mic.resume_listening()
                    print("\n=== Ready for your next sentence. ===")
                    
        except KeyboardInterrupt:
            print("\nShutting down pipeline...")
            self.mic.stop()
