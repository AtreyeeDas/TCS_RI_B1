from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

class QwenEngine:
    def __init__(self, model_path):
        print(f"[LLM] Loading Qwen2.5 from {model_path}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16,
            device_map="auto",
            local_files_only=True
        )
        
        # --- CONVERSATION STATE MANAGER ---
        self.system_prompt = (
            "You are a helpful healthcare assistant specializing in cardiovascular health. "
            "Respond concisely, empathetically, and clearly to the patient."
        )
        # Keep the last 10 messages (5 turns) to prevent VRAM explosion
        self.max_history = 10 
        self.reset_conversation()

    def reset_conversation(self):
        """Call this to clear memory when a new patient starts a session."""
        self.chat_history = [
            {"role": "system", "content": self.system_prompt}
        ]

    def generate_response(self, user_text):
        print("[LLM] Generating response with conversation history...")
        
        # 1. Add patient's new speech to memory
        self.chat_history.append({"role": "user", "content": user_text})
        
        # 2. Prune history if it gets too long (keep system prompt, slice the rest)
        if len(self.chat_history) > self.max_history + 1:
            self.chat_history = [self.chat_history[0]] + self.chat_history[-self.max_history:]

        # 3. Format with Qwen's native Chat Template
        text_prompt = self.tokenizer.apply_chat_template(
            self.chat_history,
            tokenize=False,
            add_generation_prompt=True
        )
        
        inputs = self.tokenizer([text_prompt], return_tensors="pt").to(self.model.device)
        
        # 4. Generate the response
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=150,
            temperature=0.7,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id
        )
        
        # 5. Extract just the newly generated tokens
        input_length = inputs.input_ids.shape[1]
        response_text = self.tokenizer.decode(outputs[0][input_length:], skip_special_tokens=True)
        
        # 6. Save the AI's response to memory so it remembers it next time
        self.chat_history.append({"role": "assistant", "content": response_text})
        
        return response_text
