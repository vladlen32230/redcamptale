from openai import AsyncOpenAI
import os

model_name = os.environ["MODEL_NAME"]

llm = AsyncOpenAI(
    base_url=os.environ["LLM_BASE_URL"],
    api_key=os.environ["LLM_API_KEY"]
)
