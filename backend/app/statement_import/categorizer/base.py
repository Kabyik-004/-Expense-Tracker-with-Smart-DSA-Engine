from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class CategorizationResult:
    category_name: str
    confidence: float
    method: str

    def to_dict(self):
        return {
            "category_name": self.category_name,
            "confidence": self.confidence,
            "method": self.method,
        }


class BaseCategorizer(ABC):

    @abstractmethod
    def categorize(self, description):
        pass

    @abstractmethod
    def categorize_batch(self, descriptions):
        pass

    def name(self):
        return type(self).__name__
