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
        
        # Keep the last 10 messages (5 turns) to prevent VRAM explosion
        self.max_history = 10
        self.reset_conversation()

    def reset_conversation(self):
        """Call this to clear memory when a new patient starts a session."""
        # We start with a placeholder system prompt that will be overwritten immediately on turn 1
        self.chat_history = [
            {"role": "system", "content": "You are an empathetic healthcare assistant."}
        ]

    def generate_response(self, user_text, detected_language="en"):
        print("[LLM] Generating response with conversation history...")
        
        # --- SHAPE-SHIFT PERSONA PROMPT SWITCHER ---
        if detected_language == "hi":
            active_system_prompt = (
                "You are an empathetic, human-like healthcare assistant specializing in cardiovascular health. "
                "The patient is speaking Hindi/Hinglish. You MUST respond fully in natural, conversational Hindi "
                "using ONLY the Devanagari script (e.g., 'नमस्ते', 'रक्तचाप', 'दिल'). Never use Latin/English letters "
                "for Hindi words. Keep your response comforting, highly reassuring, and concise (under 3 sentences)."
            )
        else:
            active_system_prompt = (
                "You are an empathetic, human-like healthcare assistant specializing in cardiovascular health. "
                "The patient is speaking English. You MUST respond fully in English using English letters and words. "
                "Never use Hindi or Devanagari characters. Keep your response comforting, professional, and concise (under 3 sentences)."
            )
            
        # Dynamically inject the active language rules directly into the root history slot
        if len(self.chat_history) > 0:
            self.chat_history[0] = {"role": "system", "content": active_system_prompt}
        else:
            self.chat_history.append({"role": "system", "content": active_system_prompt})

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
