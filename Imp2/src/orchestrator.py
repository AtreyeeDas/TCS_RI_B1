import asyncio
from src.audio.mic_stream import MicStream
from src.asr.seamless_s2t import SeamlessS2T
from src.llm.qwen_engine import QwenEngine
from src.guardrails.safety_net import SafetyNet
from src.tts.seamless_t2s import SeamlessT2S

class Orchestrator:
    def __init__(self):
        self.mic = MicStream()
        self.asr = SeamlessS2T()
        self.llm = QwenEngine()
        self.guardrails = SafetyNet()
        self.tts = SeamlessT2S()

    async def run_pipeline(self):
        self.mic.start_stream()
        
        try:
            while True:
                audio_chunk = self.mic.get_audio_chunk()
                
                if audio_chunk is not None:
                    print("\n[Orchestrator] Processing Audio...")
                    # 1. Walkie-Talkie Safety (Stop listening)
                    self.mic.stop_stream()
                    
                    # 2. Transcribe & Detect Language
                    text, lang = self.asr.transcribe(audio_chunk)
                    print(f"[ASR] ({lang}): {text}")
                    
                    if text.strip():
                        # 3. LLM Brain
                        raw_response = self.llm.generate_response(text, lang)
                        print(f"[LLM]: {raw_response}")
                        
                        # 4. Safety Guardrails
                        safe_response = await self.guardrails.check_response(raw_response)
                        if safe_response != raw_response:
                            print(f"[Guardrails] INTERCEPTED: {safe_response}")
                            
                        # 5. Speak
                        self.tts.speak(safe_response, lang)
                    
                    # 6. Resume Listening
                    self.mic.start_stream()
                    
                await asyncio.sleep(0.01)
                
        except KeyboardInterrupt:
            self.mic.stop_stream()
            print("\n[Orchestrator] Shutting down.")
