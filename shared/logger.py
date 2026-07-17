import logging

from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"

LOG_DIR.mkdir(exist_ok=True)


def get_logger(name):

    logger = logging.getLogger(name)

    logger.setLevel(logging.INFO)

    if logger.handlers:

        return logger

    formatter = logging.Formatter(

        "%(asctime)s | %(name)s | %(levelname)s | %(message)s"

    )

    file_handler = logging.FileHandler(

        LOG_DIR / f"{name}.log",

        encoding="utf-8"

    )

    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger