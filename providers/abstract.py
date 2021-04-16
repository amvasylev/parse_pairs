from abc import ABC, abstractmethod
from typing import Iterator, Tuple


class DataProvider(ABC):
    @classmethod
    @abstractmethod
    def _load_pairs(cls, only_traded: bool = True) -> Iterator[Tuple[str, str, str]]:
        pass
