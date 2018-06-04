import asyncio
import time
import functools
import signal
import sys
import os
from threading import Timer

import logging
from lib.core.init import init_logging

log = logging.getLogger('main')

class LoopTimer(Timer):
    def run(self):
        while True:  
            self.finished.wait(self.interval)  
            if self.finished.is_set():  
                self.finished.set()  
                break  
            self.function(*self.args, **self.kwargs) 


def read_data(loop):
    log.debug("read database begin")
    time.sleep(1)
    log.debug("read database end")
    loop.call_soon_threadsafe(save_data)

def save_data():
    log.debug("save database begin")
    time.sleep(2)
    log.debug("save database end")

def signal_handler(signum, loop):
    log.debug('received signal %d.' % signum)
    loop.call_soon_threadsafe(read_data, loop)

def timeout_handler(op_type, *args, **kwargs):
    if op_type == 'intrusion_data':
        read_data(*args, **kwargs)
    elif op_type == 'forecast':
        save_data()


if __name__ == "__main__":
    init_logging(logname='realtime_forecast', log_level=logging.DEBUG)

    loop = asyncio.get_event_loop()

    t = LoopTimer(30, functools.partial(timeout_handler, 'intrusion_data', loop))
    t.start()

    t2 = LoopTimer(35, functools.partial(timeout_handler, 'forecast', loop))
    t2.start()

    log.debug("kill -15 %d." % os.getpid())
    
    loop.add_signal_handler(signal.SIGTERM, functools.partial(signal_handler, signal.SIGTERM, loop))
    
    loop.call_soon_threadsafe(read_data, loop)

    try:
        loop.run_forever()
    finally:
        loop.close()
