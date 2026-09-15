from abc import ABC, abstractmethod

from second_brain_bot.llm.models import ChatMessage


class LLMClient(ABC):
    @abstractmethod
    def chat(
        self,
        messages: list[ChatMessage],
    ) -> str:
        ...