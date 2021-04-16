from abc import ABC, abstractmethod
from typing import Iterator, Tuple


class DataProvider(ABC):
    """Abstract class for providing data about pairs on exchange"""

    @classmethod
    @abstractmethod
    def _load_pairs(cls, only_traded: bool = True) -> Iterator[Tuple[str, str, str]]:
        """Returns iterator over tuples (exchange_pair_name, base_coin_name, quote_coin_name)"""
        pass
