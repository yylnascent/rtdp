import asyncio
import functools
import inspect
import logging
import os
import pkgutil
import signal
import sys
import time

from lib.common.abstracts import CompetitorIntrusion
from lib.common.config import Config
from lib.common.looptimer import LoopTimer
from lib.core.init import init_logging

log = logging.getLogger('main')

def fetch_data(loop, **kwargs):
    handle_module = kwargs['handle_module']
    import modules.realtime_intrusion
    package = modules.realtime_intrusion
    prefix = package.__name__ + "."
    for loader, name, ispkg in pkgutil.iter_modules(package.__path__, prefix):
        log.debug(name)
        if name.endswith(handle_module):
            module = __import__(name, globals(), locals(), ["dummy"], 0)

    for name, value in inspect.getmembers(module):
        if inspect.isclass(value) and not inspect.isabstract(value) and issubclass(value, CompetitorIntrusion) and value is not CompetitorIntrusion:
            log.debug("%s: %s."% (name, value))
            value().fetch_data(loop, **kwargs)

def save_data():
    log.debug("save database begin")
    time.sleep(2)
    log.debug("save database end")

def forecast(loop):
    log.debug("forecast begin")
    time.sleep(15)
    log.debug("forecast end")
    if not loop.is_closed():
        loop.call_soon_threadsafe(save_forecast)

def save_forecast():
    log.debug("save forecast database begin")
    time.sleep(5)
    log.debug("save forecast database end")

def signal_handler(signum, loop):
    log.debug('received signal %d.' % signum)
    loop.stop()

def fetch_timeout_handler(op_type, *args, **kwargs):
    if op_type == 'jsdb_intrusion':
        fetch_data(args[0], **kwargs)

def forecast_timeout_handler(op_type, *args, **kwargs):
    if op_type == 'jsdb_intrusion':
        forecast(args[0], **kwargs)


if __name__ == "__main__":
    init_logging(logname='realtime_forecast', log_level=logging.DEBUG)

    loop = asyncio.get_event_loop()

    config = Config()
    main_conf = config.get('main')
    log.debug('main dp_list %s' % main_conf['dp_list'])

    timer_list = []
    for sub_dp in main_conf['dp_list'].split(','):
        log.debug('sub dp %s' % sub_dp)
        sub_dp_conf = config.get(sub_dp)
        if sub_dp_conf and 'fetch_intervals' in sub_dp_conf and 'name' in sub_dp_conf:
            kwargs = {'query_sql': sub_dp_conf['query_sql'], 'handle_module': sub_dp_conf['handle_module']}
            timer_list.append(LoopTimer(int(sub_dp_conf['fetch_intervals']), functools.partial(fetch_timeout_handler, sub_dp_conf['name'], loop, **kwargs)))
        if sub_dp_conf and 'forecast_intervals' in sub_dp_conf and 'name' in sub_dp_conf:
            timer_list.append(LoopTimer(int(sub_dp_conf['forecast_intervals']), functools.partial(forecast_timeout_handler, sub_dp_conf['name'], loop)))

    for timer in timer_list:
        timer.start()

    log.debug("kill -15 %d." % os.getpid())
    
    loop.add_signal_handler(signal.SIGTERM, functools.partial(signal_handler, signal.SIGTERM, loop))
    
    try:
        loop.run_forever()
    finally:
        for timer in timer_list:
            timer.cancel()

        loop.close()
