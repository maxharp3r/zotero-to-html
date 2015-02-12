#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os

__ready__ = False

def _get_log_level():
    loglevel = os.getenv("LOG_LEVEL", "INFO")
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    return numeric_level


def _init():
    global __ready__

    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

    handler = logging.FileHandler('out/application.log')
    handler.setLevel(_get_log_level())
    handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    __ready__ = True


def get():
    if not __ready__:
        _init()
    return logging.getLogger()
