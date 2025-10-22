import logging

from pydebroglie.main import hello_world

logger = logging.getLogger(__name__)


def app() -> None:
    logger.warning(hello_world())


if __name__ == "__main__":
    app()
