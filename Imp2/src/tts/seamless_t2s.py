import torch
import torchaudio
import subprocess
import re
import os
from transformers import AutoProcessor, SeamlessM4Tv2ForTextToSpeech
from src.config import Config

class SeamlessT2S:
    def __init__(self):
        print("[TTS] Loading SeamlessM4T v2 (T2S Mode)...")
        self.processor = AutoProcessor.from_pretrained(
            Config.SEAMLESS_MODEL_PATH, 
            local_files_only=True
        )
        self.model = SeamlessM4Tv2ForTextToSpeech.from_pretrained(
            Config.SEAMLESS_MODEL_PATH, 
            torch_dtype=torch.float16,
            local_files_only=True
        ).to("cuda")
        self.model.eval()

    def speak(self, text, lang_code):
        # Sentence Chunking Bug-Fix
        sentences = re.split(r'(?<=[.!?।])\s+', text)
        
        for idx, sentence in enumerate(sentences):
            if not sentence.strip():
                continue
                
            inputs = self.processor(
                text=sentence, 
                src_lang=lang_code, 
                return_tensors="pt"
            ).to("cuda")

            with torch.no_grad():
                audio_array = self.model.generate(**inputs, tgt_lang=lang_code)[0].cpu().numpy().squeeze()

            # Save and play via ALSA natively
            filepath = f"/tmp/response_chunk_{idx}.wav"
            # Seamless outputs at 16kHz naturally
            torchaudio.save(filepath, torch.tensor(audio_array).unsqueeze(0), Config.SAMPLE_RATE)
            
            # Hardware Playback Bug-Fix (Bypass PyAudio)
            subprocess.run(["aplay", "-q", filepath])
            os.remove(filepath)
