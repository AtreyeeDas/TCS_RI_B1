import torch
from transformers import AutoProcessor, SeamlessM4Tv2ForSpeechToText
from src.config import Config

class SeamlessS2T:
    def __init__(self):
        print("[ASR] Loading SeamlessM4T v2 (S2T Mode)...")
        self.processor = AutoProcessor.from_pretrained(
            Config.SEAMLESS_MODEL_PATH, 
            local_files_only=True
        )
        self.model = SeamlessM4Tv2ForSpeechToText.from_pretrained(
            Config.SEAMLESS_MODEL_PATH, 
            torch_dtype=torch.float16,
            local_files_only=True
        ).to("cuda")
        self.model.eval()

    def transcribe(self, audio_array):
        # Convert NumPy array to PyTorch tensor
        audio_tensor = torch.tensor(audio_array).unsqueeze(0)
        
        inputs = self.processor(
            audios=audio_tensor, 
            sampling_rate=Config.SAMPLE_RATE, 
            return_tensors="pt"
        ).to("cuda", dtype=torch.float16)

        with torch.no_grad():
            output_tokens = self.model.generate(**inputs)[0]
        
        transcription = self.processor.decode(output_tokens, skip_special_tokens=True)
        
        # Heuristic/Extraction for detected language based on Seamless output tokens
        # Seamless processor naturally tags outputs; we extract it.
        # Fallback to English if parsing fails.
        detected_lang = "eng"
        try:
            lang_token = self.processor.decode(output_tokens[0:1])
            if lang_token.strip('_') in ['eng', 'hin', 'ben']:
                detected_lang = lang_token.strip('_')
        except:
            pass

        return transcription, detected_lang
