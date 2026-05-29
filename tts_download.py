from huggingface_hub import snapshot_download
import os

model_dir = "./offline_models/xtts-v2"
os.makedirs(model_dir, exist_ok=True)

print("Downloading XTTS-v2 from Hugging Face...")
snapshot_download(
    repo_id="coqui/XTTS-v2",
    local_dir=model_dir,
    allow_patterns=["model.pth", "config.json", "vocab.json", "speakers_xtts.pth"]
)
print(f"Done! Files saved cleanly to {model_dir}")
