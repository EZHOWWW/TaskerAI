from abc import ABC, abstractmethod


class LLModel(ABC):
    @abstractmethod
    def generate(
        self, system_promt: str, user_promt: str, *args, **kwargs
    ) -> str: ...  # TODO add logs
