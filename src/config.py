import os

class Config:
    # Audio Settings
    SAMPLE_RATE = 16000
    CHUNK_SIZE = 480 # 30ms for WebRTC VAD
    CHANNELS = 1
    
    # ASR Settings
    WHISPER_MODEL = "tiny.en" # Change to 'small' or 'base' for better accuracy if VRAM allows
    DEVICE = "cuda"
    COMPUTE_TYPE = "float16"
    
    # LLM Settings
    LLM_MODEL = "Qwen/Qwen2.5-3B-Instruct"
    
    # TTS Settings
    TTS_OUTPUT_DIR = "./output_audio"
    
    @classmethod
    def setup_dirs(cls):
        os.makedirs(cls.TTS_OUTPUT_DIR, exist_ok=True)
