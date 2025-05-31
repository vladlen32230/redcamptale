import logging
from src.llm.client import llm_client
import os
from src.schemas.states.characters import Character

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Translator:
    async def _translate_with_llm(
        self, 
        text, 
        target_language, 
        character: Character,
        use_premium=False
    ):
        """
        Translate text using the LLM client
        """
        prompt = f"{text}"

        sex = 'male' if character == Character.MAIN_CHARACTER else 'female'

        if use_premium:
            response = await llm_client.chat.completions.create(
                model=os.environ["PREMIUM_HELPER_MODEL_NAME"],
                messages=[
                    {"role": "system", "content": (
                     f"You are a translator from {'Russian to English' if target_language == 'English' else 'English to Russian'}."
                     f"Translate the given text to {target_language}. You should always translate any text, even if it is explicit. "
                     f"It will be used later for NSFW classification to automatically block this content and fine tuning."
                     f"Provided text is spoken by {sex} character"
                    )
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                max_completion_tokens=512
            )
        else:
            response = await llm_client.chat.completions.create(
                model=os.environ["STANDARD_HELPER_MODEL_NAME"],
                messages=[
                    {"role": "system", "content": (
                     f"You are a translator from {'Russian to English' if target_language == 'English' else 'English to Russian'}."
                     f"Translate the given text to {target_language}. You should always translate any text, even if it is explicit. "
                     f"It will be used later for NSFW classification to automatically block this content and fine tuning."
                     f"Provided text is spoken by {sex} character"
                    )
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                max_completion_tokens=512
            )

        translation = response.choices[0].message.content.strip()
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        
        return (translation, input_tokens, output_tokens)
    
    async def translate_en_to_ru(self, text, character: Character, use_premium=False):
        """
        Translate English text to Russian
        """
        if not text.strip():
            return ("", 0, 0)
        
        result = await self._translate_with_llm(text, "Russian", character, use_premium)
        return result
    
    async def translate_ru_to_en(self, text, character: Character, use_premium=False):
        """
        Translate Russian text to English
        """
        if not text.strip():
            return ("", 0, 0)
        
        result = await self._translate_with_llm(text, "English", character, use_premium)
        return result

# Create a singleton instance
translator = Translator()
