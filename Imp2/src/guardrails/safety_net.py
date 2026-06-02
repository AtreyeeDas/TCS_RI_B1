from nemoguardrails import LLMRails, RailsConfig
from src.config import Config

class SafetyNet:
    def __init__(self):
        print("[Guardrails] Initializing NeMo Safety Net...")
        config = RailsConfig.from_path(Config.GUARDRAILS_CONFIG_PATH)
        self.rails = LLMRails(config)

    async def check_response(self, text):
        # Vet the LLM output against the rules
        # In a fully offline setup without an LLM attached to the rails, 
        # this uses local embedding matching to intercept the text.
        vetted_response = await self.rails.generate_async(messages=[{
            "role": "user", "content": text
        }])
        return vetted_response["content"]
