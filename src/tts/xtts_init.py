def __init__(self, model_path, output_dir):
        print(f"[TTS] Loading XTTS-v2 into VRAM from: {model_path} ...")
        self.output_dir = output_dir
        import os # Ensure os is imported
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 1. Load Config & Model (Keep it on CPU for now)
        config_path = os.path.join(model_path, "config.json")
        self.config = XttsConfig()
        self.config.load_json(config_path)
        
        self.model = Xtts.init_from_config(self.config)
        self.model.load_checkpoint(self.config, checkpoint_dir=model_path, eval=True)
        
        # 2. Dynamic Reference Speaker Allocation (Computed on CPU to bypass Blackwell audio bug)
        from src.config import Config # Ensure Config is available
        self.speaker_audio_path = Config.SPEAKER_REFERENCE_WAV
        
        print(f"[TTS] Computing speaker embedding using profile: {self.speaker_audio_path}")
        self.gpt_cond_latent, self.speaker_embedding = self.model.get_conditioning_latents(
            audio_path=[self.speaker_audio_path]
        )
        
        # 3. NOW push the massive model to the GPU for real-time inference
        print("[TTS] Speaker profile computed. Pushing model to RTX 5000 GPU...")
        self.model.cuda()
