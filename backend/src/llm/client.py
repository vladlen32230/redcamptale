from openai import AsyncOpenAI
import os

standard_model_name = os.environ["STANDARD_MODEL_NAME"]
premium_model_name = os.environ["PREMIUM_MODEL_NAME"]

llm_client = AsyncOpenAI(
    base_url=os.environ["LLM_BASE_URL"],
    api_key=os.environ["LLM_API_KEY"]
)