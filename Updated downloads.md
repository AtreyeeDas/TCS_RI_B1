# Create the offline models directory
mkdir -p offline_models

# Copy the Qwen model from the ModelScope cache to your project
cp -r /home/spark2/.cache/modelscope/hub/models/qwen/Qwen2.5-3B-Instruct ./offline_models/
# Create the specific directory for Faster-Whisper
mkdir -p offline_models/faster-whisper-tiny.en
cd offline_models/faster-whisper-tiny.en

# Download the 4 required CTranslate2 files directly via the mirror
wget https://hf-mirror.com/Systran/faster-whisper-tiny.en/resolve/main/config.json
wget https://hf-mirror.com/Systran/faster-whisper-tiny.en/resolve/main/model.bin
wget https://hf-mirror.com/Systran/faster-whisper-tiny.en/resolve/main/tokenizer.json
wget https://hf-mirror.com/Systran/faster-whisper-tiny.en/resolve/main/vocabulary.json

# Go back to the main project folder
cd ../..
# Clone the StyleTTS2 repository into your project
git clone https://github.com/yl4579/StyleTTS2.git

# Create a folder for the base English model (LibriTTS)
mkdir -p StyleTTS2/Models/LibriTTS

# Download the checkpoint directly via the mirror
wget https://hf-mirror.com/yl4579/StyleTTS2-LibriTTS/resolve/main/Models/LibriTTS/epochs_2nd_00020.pth -O StyleTTS2/Models/LibriTTS/epochs_2nd_00020.pth
