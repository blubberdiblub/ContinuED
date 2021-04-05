#!/usr/bin/env python3

import logging as _logging
import sys as _sys

from enum import IntEnum as _IntEnum


class LogLevel(_IntEnum):

    NONE = OFF = 0
    CRITICAL = FATAL = 1
    ERROR = 2
    WARNING = WARN = 3
    NOTICE = 4
    INFO = 5
    DEBUG = 6
    TRACE = 7
    ALL = 8


locals().update(LogLevel.__members__)


_LEVEL_MAP = {
    LogLevel.NONE: 2**31 - 1,
    LogLevel.CRITICAL: _logging.CRITICAL,
    LogLevel.ERROR: _logging.ERROR,
    LogLevel.WARNING: _logging.WARNING,
    LogLevel.NOTICE: (_logging.WARNING + _logging.INFO) // 2,
    LogLevel.INFO: _logging.INFO,
    LogLevel.DEBUG: _logging.DEBUG,
    LogLevel.TRACE: (_logging.DEBUG + _logging.NOTSET) // 2,
    LogLevel.ALL: 0,
}


def basic_config(*, level: LogLevel = LogLevel.NOTICE, log4j_names=False,
                 filename=None, filemode='at'):

    _logging.addLevelName(_LEVEL_MAP[LogLevel.NOTICE], 'NOTICE')
    _logging.addLevelName(_LEVEL_MAP[LogLevel.TRACE], 'TRACE')

    if log4j_names:
        _logging.addLevelName(_LEVEL_MAP[LogLevel.CRITICAL], 'FATAL')
        _logging.addLevelName(_LEVEL_MAP[LogLevel.WARNING], 'WARN')

    # noinspection PyArgumentList
    _logging.basicConfig(
        format=(
            f'[ %(levelname)-{6 if log4j_names else 8}s ]'
            ' %(message)s'
            if level < LogLevel.TRACE else
            '%(pathname)s:%(lineno)d'
            f' [ %(levelname)-{6 if log4j_names else 8}s ]'
            ' %(asctime)s'
            ' %(message)s'
        ),
        level=_LEVEL_MAP[level],
        filename=filename,
        filemode=filemode,
        encoding='utf-8',
    )


class Logger:

    _logger: _logging.Logger

    locals().update((k, v) for k, v in LogLevel.__members__.items()
                    if LogLevel.NONE < v < LogLevel.ALL)

    def __init__(self, name: str) -> None:

        self._logger = _logging.getLogger(name)

    def _log(self, mapped_level, msg: str, *args, stacklevel: int,
             **kwargs) -> None:

        if not self._logger.isEnabledFor(mapped_level):
            return

        if args or kwargs:
            msg = msg.format(*args, **kwargs)

        self._logger.log(mapped_level, "%s", msg, stacklevel=1 + stacklevel)

    def log(self, level: LogLevel, msg: str, *args, stacklevel: int = 1,
            **kwargs) -> None:

        if not LogLevel.NONE < level < LogLevel.ALL:
            raise ValueError("invalid log level")

        self._log(_LEVEL_MAP[level], msg, *args, **kwargs,
                  stacklevel=1 + max(stacklevel, 1))

    def critical(self, msg: str, *args, stacklevel: int = 1, **kwargs) -> None:

        self._log(_LEVEL_MAP[LogLevel.CRITICAL], msg, *args, **kwargs,
                  stacklevel=1 + max(stacklevel, 1))

    def error(self, msg: str, *args, stacklevel: int = 1, **kwargs) -> None:

        self._log(_LEVEL_MAP[LogLevel.ERROR], msg, *args, **kwargs,
                  stacklevel=1 + max(stacklevel, 1))

    def warning(self, msg: str, *args, stacklevel: int = 1, **kwargs) -> None:

        self._log(_LEVEL_MAP[LogLevel.WARNING], msg, *args, **kwargs,
                  stacklevel=1 + max(stacklevel, 1))

    def notice(self, msg: str, *args, stacklevel: int = 1, **kwargs) -> None:

        self._log(_LEVEL_MAP[LogLevel.NOTICE], msg, *args, **kwargs,
                  stacklevel=1 + max(stacklevel, 1))

    def info(self, msg: str, *args, stacklevel: int = 1, **kwargs) -> None:

        self._log(_LEVEL_MAP[LogLevel.INFO], msg, *args, **kwargs,
                  stacklevel=1 + max(stacklevel, 1))

    def debug(self, msg: str, *args, stacklevel: int = 1, **kwargs) -> None:

        self._log(_LEVEL_MAP[LogLevel.DEBUG], msg, *args, **kwargs,
                  stacklevel=1 + max(stacklevel, 1))

    def trace(self, msg: str, *args, stacklevel: int = 1, **kwargs) -> None:

        self._log(_LEVEL_MAP[LogLevel.TRACE], msg, *args, **kwargs,
                  stacklevel=1 + max(stacklevel, 1))

    def exception(self, msg: str, *args, exc_info=None, stacklevel: int = 1,
                  **kwargs) -> None:

        if not self._logger.isEnabledFor(_LEVEL_MAP[LogLevel.ERROR]):
            return

        if exc_info is None:
            exc_info = _sys.exc_info()

        msg = msg.format(*args, **kwargs, exc_info=exc_info)

        self._logger.exception(
            "%s", msg, exc_info=exc_info, stacklevel=1 + max(stacklevel, 1),
        )
