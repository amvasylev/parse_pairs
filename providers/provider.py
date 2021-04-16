# built-in
from typing import List
from logging import getLogger
from typing import Iterator, Tuple

# external
import pandas as pd

# project
from .binance import BinanceProvider
from .okex import OkexProvider

logger = getLogger("providers.provider")


class PairsProvider(BinanceProvider, OkexProvider):
    def __init__(self, exchanges: List[str] = None):
        """
        :param exchanges: list of used exchanges
        """
        logger.debug(f"PairsProvider.__init__: exchanges={exchanges}")
        self._exchanges = exchanges or list()

    def load_exchange_pairs(self, exchange: str = "binance",
                            only_traded: bool = True) -> Iterator[Tuple[str, str, str]]:
        """
        Wrapper for loading pairs from single exchange
        :param exchange: exchange, which pairs to load
        :param only_traded: flag if to load only traded pairs
        :return: iterator over tuples (exchange_pair_name, base_coin_name, quote_coin_name)
        """
        logger.debug(f"PairsProvider.load_exchange_pairs: exchange={exchange}, only_traded={only_traded}")
        if exchange == "binance":
            return self.load_binance_pairs(only_traded=only_traded)
        elif exchange == "okex":
            return self.load_okex_pairs(only_traded=only_traded)
        else:
            raise NotImplementedError(f"Not implemented exchange: {exchange}")

    def load_pairs(self, only_traded: bool = True) -> pd.DataFrame:
        """
        Load full list of traded pairs
        :param only_traded: flag if to load only traded pairs
        :return: pandas.DataFrame with index `unify_name` and columns {exchange}_name with exchange pair representation
            NaN means that such pair is not presented on exchange
        """
        full_data = pd.DataFrame(columns=["unify_name"]).set_index("unify_name")
        for exchange_name in self._exchanges:
            exchange_pairs_generator = self.load_exchange_pairs(exchange=exchange_name, only_traded=only_traded)
            exchange_data = pd.DataFrame(exchange_pairs_generator, columns=[f"{exchange_name}_name", "base", "quote"])
            exchange_data["unify_name"] = exchange_data["base"] + "/" + exchange_data["quote"]
            exchange_data.drop(columns=["base", "quote"], inplace=True)
            exchange_data.set_index("unify_name", inplace=True)
            full_data = full_data.join(exchange_data, how="outer")
        return full_data

    @property
    def exchanges(self) -> List[str]:
        """Returns copy to avoid self._exchanges mutations"""
        return [exchange_name for exchange_name in self._exchanges]
