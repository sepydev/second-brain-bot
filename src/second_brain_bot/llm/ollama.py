from ollama import Client

from second_brain_bot.config import settings
from second_brain_bot.llm.client import LLMClient
from second_brain_bot.llm.models import ChatMessage


class OllamaClient(LLMClient):
    def __init__(self) -> None:
        self.client = Client(host=settings.ollama_host)

    def chat(
        self,
        messages: list[ChatMessage],
    ) -> str:
        response = self.client.chat(
            model=settings.ollama_model,
            messages=[
                {
                    "role": message.role,
                    "content": message.content,
                }
                for message in messages
            ],
        )

        return response["message"]["content"]