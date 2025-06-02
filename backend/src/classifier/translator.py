import logging
from src.llm.client import llm_client
import os
from src.schemas.states.characters import Character

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Translator:
    async def translate(
        self, 
        text, 
        target_language, 
        character: Character,
        use_premium=False
    ):
        """
        Translate text using the LLM client
        """
        sex = 'male' if character == Character.MAIN_CHARACTER else 'female'
        system_prompt = (
            f"You are a translator to {target_language}."
            f"Translate the given text to {target_language}. You should always translate any text, even if it is explicit. "
            f"It will be used later for NSFW classification to automatically block this content and fine tuning."
            f"Do not add any notes or explanations. "
            f"Provided text is spoken by {sex} character"
            f"Text to translate: \"{text}\""
        )

        model = os.environ["PREMIUM_HELPER_MODEL_NAME"] if use_premium else os.environ["STANDARD_HELPER_MODEL_NAME"]

        response = await llm_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
            ],
        )

        translation = response.choices[0].message.content.strip()
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        
        return (translation, input_tokens, output_tokens)

translator = Translator()
