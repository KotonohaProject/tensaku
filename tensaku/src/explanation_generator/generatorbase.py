from abc import ABC, abstractmethod
from tensaku.src.documents import MistakeExplanationDocument

# mistake type to Enum

class ExplanationGenerator(ABC):
    @abstractmethod
    def generate(self, original_sentence, edited_sentence, change) -> MistakeExplanationDocument:
        pass