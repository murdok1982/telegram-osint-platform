import openai
import os
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    def __init__(self, model: str = "gpt-4"):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY environment variable is required")
        self.model = model
        self.client = openai.OpenAI(api_key=self.api_key)

    @abstractmethod
    def analyze(self, input_data: str) -> str:
        pass

    def _call_llm(self, system_prompt: str, user_content: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.3,
                max_tokens=2000,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise
