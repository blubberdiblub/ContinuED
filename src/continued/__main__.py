#!/usr/bin/env python3

import sys

import qtrio

from . import main
from . import logging


if all(sys.breakpointhook is not _ for _ in (None, sys.__breakpointhook__)):
    logging.basic_config(level=logging.LogLevel.TRACE, log4j_names=True,
                         filename='debug.log', filemode='wt')
    logging._logging.getLogger('watchgod.main').setLevel(30)

elif __debug__ or sys.flags.dev_mode:
    logging.basic_config(level=logging.LogLevel.DEBUG, log4j_names=True,
                         filename='debug.log', filemode='wt')
    logging._logging.getLogger('watchgod.main').setLevel(30)

else:
    logging.basic_config(level=logging.LogLevel.NOTICE, log4j_names=True)


qtrio.run(main.loop)
