#!/usr/bin/env python

import logging
import time

# configure logging
logging.basicConfig(
    filename='radcast.log',
    format='%(levelname)s: %(message)s',
    filemode="w",
    level=logging.DEBUG
)
logging.info("Started %s" % time.strftime("%a, %d %b %Y %T %Z"))
