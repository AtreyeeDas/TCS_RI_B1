import os
import torch
import wave
import pyaudio
import torchaudio
import torchaudio.functional as F
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
        clean_text = text.replace("*", "").replace("#", "").strip()
        if not clean_text:
            return

        print(f"[TTS] Synthesizing ({language}): '{clean_text[:50]}...'")
        output_path = os.path.join(self.output_dir, "current_response.wav")
        
        # Generate raw audio at native 24000 Hz
        out = self.model.inference(
            text=clean_text,
            language=language,
            gpt_cond_latent=self.gpt_cond_latent,
            speaker_embedding=self.speaker_embedding,
            temperature=0.7,
        )
        
        # Convert to tensor
        audio_tensor = torch.tensor(out["wav"]).unsqueeze(0)
        
        # Resample from native 24000 Hz to hardware-compatible 16000 Hz
        print("[TTS] Resampling audio to 16000 Hz for hardware compatibility...")
        audio_resampled = F.resample(audio_tensor, orig_freq=24000, new_freq=16000)
        
        # Save the 16kHz wave file
        torchaudio.save(output_path, audio_resampled, 16000)
        
        # Play via PyAudio
        self._play_audio(output_path)

    def _play_audio(self, filepath):
        print("[TTS] 🔊 Speaking...")
        wf = wave.open(filepath, 'rb')
        p = pyaudio.PyAudio()
        
        # Open stream explicitly matching your system's working sample rate
        stream = p.open(
            format=p.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(), # This will now be 16000 Hz
            output=True
        )
        
        data = wf.readframes(1024)
        while data:
            stream.write(data)
            data = wf.readframes(1024)
            
        stream.stop_stream()
        stream.close()
        p.terminate()
