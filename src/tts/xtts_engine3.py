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
        
        # --- NEW: Dynamic Hardware Interrogation ---
        p = pyaudio.PyAudio()
        device_info = p.get_default_output_device_info()
        self.hardware_sample_rate = int(device_info['defaultSampleRate'])
        print(f"[TTS] 🎧 Hardware playback rate dynamically set to: {self.hardware_sample_rate} Hz")
        p.terminate()
        # -------------------------------------------
        
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
        
        # Generate raw audio at XTTS native 24000 Hz
        out = self.model.inference(
            text=clean_text,
            language=language,
            gpt_cond_latent=self.gpt_cond_latent,
            speaker_embedding=self.speaker_embedding,
            temperature=0.7,
        )
        
        # Convert to tensor
        audio_tensor = torch.tensor(out["wav"]).unsqueeze(0)
        
        # --- NEW: Dynamic Resampling ---
        # Resample from 24000 to whatever your specific hardware demands
        if self.hardware_sample_rate != 24000:
            audio_tensor = F.resample(audio_tensor, orig_freq=24000, new_freq=self.hardware_sample_rate)
        
        # Save the hardware-safe wave file
        torchaudio.save(output_path, audio_tensor, self.hardware_sample_rate)
        
        # Play via PyAudio
        self._play_audio(output_path)

    def _play_audio(self, filepath):
        print("[TTS] 🔊 Speaking...")
        wf = wave.open(filepath, 'rb')
        p = pyaudio.PyAudio()
        
        # Open stream using the exact framerate from the saved WAV file
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
