from abc import ABC, abstractmethod
from pydantic import BaseModel


class LLModel(ABC):
    @abstractmethod
    def generate(
        self, system_promt: str, user_promt: str, *args, **kwargs
    ) -> str: ...  # TODO add logs


class ModelRequest(BaseModel):
    system_promt: str = ""
    user_promt: str = ""
