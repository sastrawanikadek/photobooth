import asyncio
import logging

import colorlog
import uvloop
from constants import APP_ENV
from core import Photobooth
from enums import Environment
from events import AppReadyEvent


async def main() -> None:
    photobooth = Photobooth()
    photobooth.component_manager.load_preinstalled()
    photobooth.eventbus.dispatch(AppReadyEvent({"message": "The app is ready."}))

    await asyncio.Future()


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
