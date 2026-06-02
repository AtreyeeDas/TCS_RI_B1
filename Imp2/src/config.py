import os

class Config:
    # --- Offline Model Paths ---
    # FILL THESE PATHS IN ONCE MODELS ARE TRANSFERRED
    SEAMLESS_MODEL_PATH = "./offline_models/seamless-m4t-v2-large"
    QWEN_MODEL_PATH = "./offline_models/qwen2.5-3b-instruct"
    SILERO_VAD_PATH = "./offline_models/silero-vad-master"
    GUARDRAILS_CONFIG_PATH = "./src/guardrails" 
    
    # --- Audio Parameters ---
    SAMPLE_RATE = 16000
    CHUNK_SIZE = 1024
    INPUT_DEVICE_INDEX = 7  # Bound strictly to sof-soundwire
    
    # --- VAD Constraints ---
    SILENCE_THRESHOLD = 1.5  # Seconds of silence to trigger pipeline
    GHOST_NOISE_THRESHOLD = 8000  # Elements (0.5s). Drop if smaller.
    
    # --- Generation Constraints ---
    MAX_NEW_TOKENS = 150
    TEMPERATURE = 0.7
