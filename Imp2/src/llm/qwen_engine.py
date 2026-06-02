import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from src.config import Config

class QwenEngine:
    def __init__(self):
        print("[LLM] Loading Qwen 2.5 3B...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            Config.QWEN_MODEL_PATH, 
            local_files_only=True
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            Config.QWEN_MODEL_PATH,
            torch_dtype=torch.float16,
            device_map="cuda",
            local_files_only=True
        )
        self.chat_history = [{"role": "system", "content": ""}]
        
        self.en_prompt = "You are a professional cardiovascular doctor. Be empathetic, concise, and provide clinical advice in English."
        self.hin_prompt = "आप एक पेशेवर हृदय रोग विशेषज्ञ हैं। केवल देवनागरी लिपि का उपयोग करें, सहानुभूतिपूर्ण रहें और हिंदी चिकित्सा शब्दावली का उपयोग करें।"

    def generate_response(self, text, lang_code):
        # 1. Dynamic Prompt Swapping (Zero-Bleed)
        if lang_code == "hin":
            self.chat_history[0]["content"] = self.hin_prompt
        else:
            self.chat_history[0]["content"] = self.en_prompt

        # 2. Append User Message
        self.chat_history.append({"role": "user", "content": text})

        # 3. Prune Memory (Cap at 10 to save VRAM, keep index 0)
        while len(self.chat_history) > 10:
            self.chat_history.pop(1)

        # 4. Generate
        text_inputs = self.tokenizer.apply_chat_template(
            self.chat_history,
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to("cuda")

        with torch.no_grad():
            generated_ids = self.model.generate(
                text_inputs, 
                max_new_tokens=Config.MAX_NEW_TOKENS, 
                temperature=Config.TEMPERATURE
            )
            
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(text_inputs, generated_ids)
        ]
        
        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        
        # Append AI response to history
        self.chat_history.append({"role": "assistant", "content": response})
        
        return response
