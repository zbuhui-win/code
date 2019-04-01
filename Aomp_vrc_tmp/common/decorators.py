#!/usr/bin/env python

import time
from functools import wraps
import logging.config
logger = logging.getLogger()


def exeTime(func):
    """
        交易耗时测算装饰器，by wuyunzhen.zh  20181208
    """
    @wraps(func)
    def print_time(*args, **args2):
        t0 = time.time()
        back = func(*args, **args2)
        logger.info("@%.3fs taken for {%s}" % (time.time() - t0, func.__name__))
        return back
    return print_time


def addlog(func):
    """
        交易耗时测算装饰器，by wuyunzhen.zh  20181208
    """
    @wraps(func)
    def add_log(*args, **args2):
        logger.info("{%s} start" %func.__name__ )
        back = func(*args, **args2)
        logger.info("{%s} end" %func.__name__)
        return back
    return add_log