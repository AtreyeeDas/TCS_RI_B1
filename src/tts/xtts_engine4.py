import os
import torch
import torchaudio
import subprocess
import re
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
from src.config import Config

class MultilingualTTSEngine:
    def __init__(self, model_path, output_dir):
        print(f"[TTS] Loading XTTS-v2 into VRAM from: {model_path} ...")
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 1. Load Config & Model
        config_path = os.path.join(model_path, "config.json")
        self.config = XttsConfig()
        self.config.load_json(config_path)
        
        self.model = Xtts.init_from_config(self.config)
        self.model.load_checkpoint(self.config, checkpoint_dir=model_path, eval=True)
        self.model.cuda() 
        
        # 2. Dynamic Reference Speaker Allocation
        self.speaker_audio_path = Config.SPEAKER_REFERENCE_WAV 
        
        print(f"[TTS] Computing speaker embedding using profile: {self.speaker_audio_path}")
        self.gpt_cond_latent, self.speaker_embedding = self.model.get_conditioning_latents(
            audio_path=[self.speaker_audio_path]
        )

    def synthesize_and_play(self, text, language="en"):
        # Strip markdown that confuses the TTS engine
        clean_text = text.replace("*", "").replace("#", "").strip()
        if not clean_text:
            return

        # CHUNKING LOGIC: Split paragraph into sentences by punctuation (. ! ? or Hindi purna viram ।)
        # The regex splits after punctuation and spaces, keeping the sentences intact
        sentences = re.split(r'(?<=[.!?।])\s+', clean_text)

        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence:
                continue

            # Fallback: If a single run-on sentence is somehow still > 230 chars, split it by commas
            if len(sentence) > 230:
                chunks = sentence.split(',')
            else:
                chunks = [sentence]

            for j, chunk in enumerate(chunks):
                chunk = chunk.strip()
                if not chunk:
                    continue
                    
                print(f"[TTS] Synthesizing Part {i+1} ({language}): '{chunk[:40]}...'")
                output_path = os.path.join(self.output_dir, "current_response.wav")
                
                # Generate audio chunk at XTTS native 24000 Hz
                out = self.model.inference(
                    text=chunk,
                    language=language,
                    gpt_cond_latent=self.gpt_cond_latent,
                    speaker_embedding=self.speaker_embedding,
                    temperature=0.7,
                )
                
                audio_tensor = torch.tensor(out["wav"]).unsqueeze(0)
                
                # Save chunk to disk
                torchaudio.save(output_path, audio_tensor, 24000)
                
                # Play immediately using the native Linux aplay tool
                self._play_audio(output_path)

    def _play_audio(self, filepath):
        print("[TTS] 🔊 Speaking...")
        # BYPASS PYAUDIO: Call the native Linux aplay tool in the background
        # The '-q' flag keeps the terminal clean from ALSA warnings
        subprocess.run(["aplay", "-q", filepath])
