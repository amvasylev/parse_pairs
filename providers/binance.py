# built-in
from logging import getLogger
from typing import Iterator, Tuple

# external
from requests import get as GET

# project
from .abstract import DataProvider

logger = getLogger("providers.binance")


class BinanceProvider(DataProvider):
    _basic_url = "https://api.binance.com"
    _pairs_endpoint = "/api/v3/exchangeInfo"

    @classmethod
    def _load_pairs(cls, only_traded: bool = True) -> Iterator[Tuple[str, str, str]]:
        full_url = cls._basic_url + cls._pairs_endpoint
        response = GET(full_url)
        if response.status_code != 200:
            message = f"Binance request {full_url}"
            message += f". Response code: {response.status_code}"
            message += f". Error: {response.text}"
            logger.error(message)
            return

        response_json = response.json()
        try:
            all_pairs = response_json["symbols"]
            logger.info(f"Binance total pairs: {len(all_pairs)}")
        except KeyError:
            logger.error("There is no `symbols` at Binance exchangeInfo")
            return

        for pair_info in all_pairs:
            try:
                exchange_pair_name = pair_info["symbol"]
                base = pair_info["baseAsset"]
                quote = pair_info["quoteAsset"]
                status = pair_info["status"]
            except KeyError:
                message = "Missed one of mandatory fields: (`symbol`, `baseAsset`, `quoteAsset`, `status`)"
                message += f". Bad pair: {pair_info.get('symbol', None)}"
                logger.error(message)
                continue
            if status == "TRADING":
                yield exchange_pair_name, base, quote
            elif only_traded:
                logger.warning(f"Untradeable pair: {exchange_pair_name} with status={status}")
            else:
                yield exchange_pair_name, base, quote

    @staticmethod
    def load_binance_pairs(only_traded: bool = True):
        return BinanceProvider._load_pairs(only_traded=only_traded)
