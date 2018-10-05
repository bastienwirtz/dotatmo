#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import time, sys, socket
import signal
import math

from dotatmo import Dotatmo
dotatmo = Dotatmo()

# Sigterm handler
def sigterm_handler(_signo, _stack_frame):
    global dotatmo
    dotatmo.stop()

signal.signal(signal.SIGTERM, sigterm_handler)


if __name__ == '__main__':
    try:
        dotatmo.start()
    except KeyboardInterrupt:
        dotatmo.stop()
