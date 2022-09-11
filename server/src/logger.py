"""Configure handlers and formats for application loggers."""
import logging
import sys
import json
import os.path as path

from pprint import pformat
from loguru import logger


class InterceptHandler(logging.Handler):
    """
    Default handler from examples in loguru documentaion.
    See https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging # noqa: E501
    """

    def emit(self, record: logging.LogRecord):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


class Formatter:
    def __init__(self, format: str = None):
        self.padding = 30
        self.fmt = format or (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>"
            " | <level>{level: <8}</level>"
            " | {process: <5}"
            " | <cyan>{name}:{function}:{line}{extra[padding]}</cyan>"
            " - <level>{message}</level>"
        )

    def format(self, record: dict) -> str:
        """
        Custom format for loguru loggers.
        Dynamic padding for {name}:{function}:{line}
        Uses pformat for log any data like request/response body during debug.
        Works with logging if loguru handler it.
        Example:
        >>> payload = [{"users":[{"name": "Nick", "age": 87, "is_active": True}, {"name": "Alex", "age": 27, "is_active": True}], "count": 2}] # noqa: E501s
        >>> logger.bind(payload=).debug("users payload")
        >>> [   {   'count': 2,
        >>>         'users': [   {'age': 87, 'is_active': True, 'name': 'Nick'},
        >>>                      {'age': 27, 'is_active': True, 'name': 'Alex'}]}]
        """
        format_string = self.fmt

        length = len("{name}:{function}:{line}".format(**record))
        self.padding = max(self.padding, length)
        record["extra"]["padding"] = " " * (self.padding - length)

        if record["extra"].get("payload") is not None:
            record["extra"]["payload"] = pformat(
                record["extra"]["payload"], indent=2, compact=False, width=120
            )

            format_string += "\n<level>{extra[payload]}</level>"

        format_string += "{exception}\n"
        return format_string


def init_logger(file: str, modules: list):
    """
    Replaces logging handlers with a handler for using the custom handler.

    WARNING!
    if you call the init_logging in startup event function,
    then the first logs before the application start will be in the old format
    >>> app.add_event_handler("startup", init_logging)
    stdout:
    INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
    INFO:     Started reloader process [11528] using statreload
    INFO:     Started server process [6036]
    INFO:     Waiting for application startup.
    2020-07-25 02:19:21.357 | INFO     | uvicorn.lifespan.on:startup:34 - Application startup complete. # noqa: E501

    """

    # get logger for the 'modules'
    loggers = (
        logging.getLogger(name)
        for name in logging.root.manager.loggerDict
        if name.startswith(tuple(modules))
    )

    # disable handlers for the logger and propagete to its parent
    for remove_logger in loggers:
        remove_logger.handlers = []
        remove_logger.propagate = True

    intercept_handler = InterceptHandler()

    # change handler for logger and stop propgate
    for name in modules:
        logging.getLogger(name).handlers = [intercept_handler]
        logging.getLogger(name).propagate = False

    # also intercept root logger
    logging.getLogger().handlers = [intercept_handler]

    # read logger configuration from the file
    # otherwise log to stdout
    if path.exists(file):
        logconfig = json.load(open(file))

        for config in logconfig:
            config["sink"] = (
                sys.stdout if config["sink"] == "stdout" else config["sink"]
            )
            config["format"] = (
                Formatter(config["format"]).format
                if "format" in config
                else Formatter().format
            )
    else:
        logconfig = [
            {
                "sink": sys.stdout,
                "level": logging.DEBUG,
                "format": Formatter().format,
            },
        ]

    # set logs output, level and format
    logger.configure(handlers=logconfig)
