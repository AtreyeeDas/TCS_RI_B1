from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

class QwenEngine:
    def __init__(self, model_name):
        print(f"[LLM] Loading Qwen2.5 ({model_name})...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        # Using 8-bit quantization for lower VRAM usage
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            load_in_8bit=True
        )
        
        self.system_prompt = (
            "You are a helpful healthcare assistant specializing in cardiovascular health. "
            "Respond concisely and clearly to the patient's transcription."
        )

    def generate_response(self, text):
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": text}
        ]
        
        text_input = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        model_inputs = self.tokenizer([text_input], return_tensors="pt").to(self.model.device)
        
        print("[LLM] Generating response...")
        generated_ids = self.model.generate(
            **model_inputs,
            max_new_tokens=150,
            pad_token_id=self.tokenizer.eos_token_id
        )
        
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]
        
        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return response.strip()
