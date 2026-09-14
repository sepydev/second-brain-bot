from abc import ABC, abstractmethod

from telegram import Update
from telegram.ext import ContextTypes


class Command(ABC):
    name: str
    description: str

    @abstractmethod
    async def execute(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        ...
