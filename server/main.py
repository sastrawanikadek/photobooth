import logging

import colorlog
import uvloop

from server.constants import APP_ENV
from server.core import Photobooth
from server.enums import Environment


async def main() -> None:
    photobooth = Photobooth()
    photobooth.initialize()
    photobooth.prepare()
    await photobooth.startup()


def setup_logging() -> None:
    logging_level = (
        logging.DEBUG
        if APP_ENV in [Environment.LOCAL, Environment.DEV]
        else logging.INFO
    )

    formatter = colorlog.ColoredFormatter(
        "%(log_color)s[%(asctime)s] %(name)s -> %(levelname)s: %(message)s",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red,bg_white",
        },
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logging.basicConfig(level=logging_level, handlers=[handler])


if __name__ == "__main__":
    setup_logging()
    uvloop.run(main())
