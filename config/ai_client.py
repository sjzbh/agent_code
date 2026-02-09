import openai
from config.settings import settings

class LLMClient:
    def __init__(self):
        # 只要填入 .env 里的那三个要素，这里不需要管是 DeepSeek 还是 OpenAI
        self.client = openai.OpenAI(
            api_key=settings.API_KEY,
            base_url=settings.BASE_URL
        )

    def ask(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7
        )
        return response.choices[0].message.content