import time
from src.config import Config
from src.audio.mic_stream import MicStream
from src.asr.streaming_whisper import StreamingWhisper
from src.llm.qwen_engine import QwenEngine
from src.tts.styletts_engine import StyleTTSEngine

class PipelineOrchestrator:
    def __init__(self):
        Config.setup_dirs()
        self.mic = MicStream(Config.SAMPLE_RATE, Config.CHUNK_SIZE)
        self.asr = StreamingWhisper(Config.WHISPER_MODEL, Config.DEVICE, Config.COMPUTE_TYPE)
        self.llm = QwenEngine(Config.LLM_MODEL)
        self.tts = StyleTTSEngine(Config.TTS_OUTPUT_DIR)
        
    def run(self):
        self.mic.start()
        print("\n=== Pipeline Active. Start speaking. Press Ctrl+C to stop. ===\n")
        
        try:
            while True:
                time.sleep(0.1) # Small sleep to prevent CPU hogging
                chunk = self.mic.get_audio_chunk()
                
                final_text, partial_text = self.asr.process_chunk(chunk)
                
                if partial_text:
                    print(f"\r[ASR Partial]: {partial_text}", end="")
                    
                if final_text:
                    print(f"\n[ASR Final]: {final_text}")
                    
                    # Pause mic processing while LLM and TTS run (Half-Duplex mode for Phase 1)
                    llm_response = self.llm.generate_response(final_text)
                    print(f"[LLM Output]: {llm_response}")
                    
                    self.tts.synthesize(llm_response)
                    print("-" * 50)
                    
        except KeyboardInterrupt:
            print("\nShutting down pipeline...")
        finally:
            self.mic.stop()
