import asyncio
import functools
import inspect
import logging
import os
import pkgutil
import schedule
import signal
import sys
import time

from lib.common.abstracts import CompetitorIntrusion
from lib.common.exceptions import RTDPConfigurationError
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

def signal_handler(signum, loop):
    log.debug('received signal %d.' % signum)
    loop.stop()

def fetch_timeout_handler(*args, **kwargs):
    fetch_data(args[0], **kwargs)

def exception_handler(context):
    log.error('got exception with error messages: \n%s' % context['message'])

    if isinstance(context['exception'], RTDPConfigurationError):
        raise context['exception']

def init_timer(loop, conf):
    main_conf = config.get('main')
    log.debug('main dp_list %s' % main_conf['dp_list'])

    timer_list = []
    for sub_dp in main_conf['dp_list'].split(','):
        log.debug('sub dp %s' % sub_dp)
        sub_dp_conf = config.get(sub_dp)
        base_fetch_intervals = sub_dp_conf['fetch_intervals'] if 'fetch_intervals' in sub_dp_conf else None
        base_handle_module = sub_dp_conf['handle_module'] if 'handle_module' in sub_dp_conf else None
        for module in sub_dp_conf['module_name'].split(','):
            log.debug('sub module %s' % module)
            module_name_conf = config.get(module)
            if module_name_conf:
                fetch_intervals = module_name_conf['fetch_intervals'] if 'fetch_intervals' in module_name_conf else base_fetch_intervals
                handle_module = module_name_conf['handle_module'] if 'handle_module' in module_name_conf else base_handle_module
                if fetch_intervals and handle_module:
                    kwargs = {'query_sql': module_name_conf['query_sql'], 'handle_module': handle_module, 'module_tag':module}
                    # schedule.every(int(fetch_intervals)).seconds.do(fetch_timeout_handler, loop, **kwargs)
                    timer_list.append(LoopTimer(int(fetch_intervals), functools.partial(fetch_timeout_handler, loop, **kwargs)))
                else:
                    log.error('dataprocess <%s>\'s <%s> module does not specify fetch_intervals or handle_module' % (sub_dp, module))
                    timer_list = []
                    raise RTDPConfigurationError('dataprocess <%s>\'s <%s> module does not specify fetch_intervals or handle_module' % (sub_dp, module))    

    return timer_list


if __name__ == "__main__":
    init_logging(logname='realtime_forecast', log_level=logging.DEBUG)

    loop = asyncio.get_event_loop()

    config = Config(file_name="dataprocess")

    timer_list = init_timer(loop, config)
    for timer in timer_list:
        timer.set_exception_handler(exception_handler)
        timer.start()

    log.debug("kill -15 %d." % os.getpid())
    
    loop.add_signal_handler(signal.SIGTERM, functools.partial(signal_handler, signal.SIGTERM, loop))
    
    try:
        loop.run_forever()
        while True:
            schedule.run_pending()
            time.sleep(1)
    finally:
        for timer in timer_list:
            timer.cancel()

        loop.close()
