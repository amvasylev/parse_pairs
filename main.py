#!/usr/bin/env python3

# built-in
import argparse
import logging
from sys import argv
from providers import PairsProvider
import toml
from pathlib import Path
import os
from datetime import datetime

logger = logging.getLogger("__main__")


def _parse_args():
    parser = argparse.ArgumentParser(description="Load pairs")
    parser.add_argument("--config", dest="config_name", action="store", default="default",
                        help="Filename of global config")
    parser.add_argument("--terminal", dest="into_terminal", action="store_true",
                        help="Flag if to dump results into terminal")
    args = argv[1:]
    args = parser.parse_args(args)
    kwargs = dict(args._get_kwargs())
    return kwargs


def _set_logging(config):
    logging_config = config.get("logging", dict())
    filename = logging_config.get("filename", "log")
    now = int(datetime.utcnow().timestamp())
    filename = f"{filename}_{now}.txt"
    logging_config["filename"] = "./logs" / Path(filename)
    os.makedirs(Path(logging_config["filename"]).parent, exist_ok=True)
    logging.basicConfig(**logging_config)
    del config["logging"]


def _load_data(config):
    provider_config = config.get("provider", dict())
    exchanges = provider_config.get("exchanges")
    only_traded = provider_config.get("only_traded", False)
    logger.debug(f"Provider config: {provider_config}")
    pairs_provider = PairsProvider(exchanges)
    data = pairs_provider.load_pairs(only_traded=only_traded)
    logger.info(f"Loaded pairs. Total exchanges: {len(pairs_provider.exchanges)}, data shape: {data.shape}")
    return data


def _dump_all(config, data):
    dumps_config = config.get("dumps", dict())
    csv_filename = dumps_config.get("filename", "pairs") + ".csv"
    dump_path = "./data" / Path(csv_filename)
    logger.debug(f"Will dump into {dump_path}")
    os.makedirs(dump_path.parent, exist_ok=True)
    data.to_csv(dump_path)


def _dump_into_terminal(data, into_terminal: bool):
    if into_terminal:
        print(data.index.name, *data.columns)
        for running_tuple in data.itertuples():
            print(*running_tuple)


def main():
    kwargs = _parse_args()
    config_name = kwargs["config_name"] + ".toml"

    try:
        config = toml.load(f"./settings/{config_name}")
    except FileNotFoundError:
        logger.error(f"No such config: ./settings/{config_name}. Please, add it or choose `--config default`")
        return

    _set_logging(config=config)
    logger.info(f"Script kwargs: {kwargs}. Global config: {config}")
    data = _load_data(config=config)
    _dump_into_terminal(data, kwargs["into_terminal"])
    _dump_all(config=config, data=data)


if __name__ == "__main__":
    main()
