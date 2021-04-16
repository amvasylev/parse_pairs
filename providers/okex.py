# built-in
from logging import getLogger
from typing import Iterator, Tuple

# external
from requests import get as GET

# project
from .abstract import DataProvider

logger = getLogger("providers.okex")


class OkexProvider(DataProvider):
    _basic_url = "https://www.okex.com"
    _pairs_endpoint = "/api/spot/v3/instruments"

    @classmethod
    def _load_pairs(cls, only_traded: bool = True) -> Iterator[Tuple[str, str, str]]:
        full_url = cls._basic_url + cls._pairs_endpoint
        response = GET(full_url)
        if response.status_code != 200:
            message = f"Okex request {full_url}"
            message += f". Response code: {response.status_code}"
            message += f". Error: {response.text}"
            logger.error(message)
            return

        all_pairs = response.json()
        logger.info(f"Okex total pairs: {len(all_pairs)}")

        for pair_info in all_pairs:
            try:
                exchange_pair_name = pair_info["instrument_id"]
                base = pair_info["base_currency"]
                quote = pair_info["quote_currency"]
            except KeyError:
                message = "Missed one of mandatory fields: (`instrument_id`, `base_currency`, `quote_currency`)"
                message += f". Bad pair: {pair_info.get('symbol', None)}"
                logger.error(message)
                continue
            yield exchange_pair_name, base, quote

    @staticmethod
    def load_okex_pairs(only_traded: bool = True):
        return OkexProvider._load_pairs(only_traded=only_traded)
