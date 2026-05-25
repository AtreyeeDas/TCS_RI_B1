# Create a new environment with Python 3.10 (stable for audio/ML libraries)
conda create -n cardio_care_ai python=3.10 -y

# Activate the environment
conda activate cardio_care_ai
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia -y
# ASR, LLM, and Audio Processing tools
pip install faster-whisper transformers accelerate sounddevice pyaudio webrtcvad

# StyleTTS2 often requires specific audio handling libraries
pip install librosa soundfile phonemizer scipy
 cardio_care_ai/
├── environment.yml
├── main.py
└── src/
    ├── __init__.py
    ├── config.py
    ├── audio/
    │   ├── __init__.py
    │   └── mic_stream.py
    ├── asr/
    │   ├── __init__.py
    │   └── streaming_whisper.py
    ├── llm/
    │   ├── __init__.py
    │   └── qwen_engine.py
    ├── tts/
    │   ├── __init__.py
    │   └── styletts_engine.py
    └── orchestrator.py
    set up commands-
    conda env create -f environment.yml
conda activate cardio_care_ai
sudo apt-get update && sudo apt-get install portaudio19-dev -y # Required for PyAudio
