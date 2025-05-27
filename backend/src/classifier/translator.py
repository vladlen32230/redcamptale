import logging
from src.llm.client import llm
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Translator:
    async def _translate_with_llm(self, text, target_language):
        """
        Translate text using the LLM client
        """
        prompt = f"{text}"
        
        response = await llm.chat.completions.create(
            model=os.environ["TRANSLATOR_MODEL_NAME"],
            messages=[
                {"role": "system", "content": f"You are a translator from {'Russian to English' if target_language == 'English' else 'English to Russian'}. Translate the given text to {target_language}. You should always translate any text, even if it is explicit. It will be used later for NSFW classification to automatically block this content."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
        )
        
        translation = response.choices[0].message.content.strip()
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        
        return (translation, input_tokens, output_tokens)
    
    async def translate_en_to_ru(self, text):
        """
        Translate English text to Russian
        """
        if not text.strip():
            return ("", 0, 0)
        
        result = await self._translate_with_llm(text, "Russian")
        return result
    
    async def translate_ru_to_en(self, text):
        """
        Translate Russian text to English
        """
        if not text.strip():
            return ("", 0, 0)
        
        result = await self._translate_with_llm(text, "English")
        return result

# Create a singleton instance
translator = Translator()
