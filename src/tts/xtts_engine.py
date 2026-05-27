import os
import torch
import wave
import pyaudio
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts

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
        self.model.cuda() # Send to your RTX 5000
        
        # 2. Set up Voice Cloning (Requires a 5-second sample wav)
        self.speaker_audio_path = "./doctor_voice.wav" 
        if not os.path.exists(self.speaker_audio_path):
            print(f"\n[WARNING] {self.speaker_audio_path} not found! TTS will crash. Please add a 5-second voice sample.")
            
        print("[TTS] Computing speaker embedding for voice cloning...")
        self.gpt_cond_latent, self.speaker_embedding = self.model.get_conditioning_latents(
            audio_path=[self.speaker_audio_path]
        )

    def synthesize_and_play(self, text, language="en"):
        # XTTS struggles with markdown asterisks and hashtags; strip them out
        clean_text = text.replace("*", "").replace("#", "").strip()
        if not clean_text:
            return

        print(f"[TTS] Synthesizing ({language}): '{clean_text[:50]}...'")
        output_path = os.path.join(self.output_dir, "current_response.wav")
        
        # Generate Audio
        out = self.model.inference(
            text=clean_text,
            language=language,
            gpt_cond_latent=self.gpt_cond_latent,
            speaker_embedding=self.speaker_embedding,
            temperature=0.7,
        )
        
        # Save Audio
        import torchaudio
        audio_tensor = torch.tensor(out["wav"]).unsqueeze(0)
        torchaudio.save(output_path, audio_tensor, 24000)
        
        # Play Audio Live
        self._play_audio(output_path)

    def _play_audio(self, filepath):
        print("[TTS] 🔊 Speaking...")
        wf = wave.open(filepath, 'rb')
        p = pyaudio.PyAudio()
        stream = p.open(
            format=p.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(),
            output=True
        )
        
        data = wf.readframes(1024)
        while data:
            stream.write(data)
            data = wf.readframes(1024)
            
        stream.stop_stream()
        stream.close()
        p.terminate()
