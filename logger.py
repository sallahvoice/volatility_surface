import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

log_path = Path(__file__).parent / "logs.log"
log_path.mkdir(parents=True, exist_ok=True)


def setup_logger(name: str):
    logger = logging.getLogger(name)
    logger.propagate(False)
    logger.setLevel(logging.Info)

    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler = RotatingFileHandler(
            log_path, maxBytes=2 * 1024 * 1024, backupCount=3, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)

        stream_hanlder = logging.StreamHandler()
        stream_hanlder.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(stream_hanlder)

    return logger


def get_logger(name: str):
    return setup_logger(name)
