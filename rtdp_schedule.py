import inspect
import logging
import multiprocessing
import pkgutil
import schedule
import signal
import time

import modules.data_etl

from lib.common.abstracts import CommonETL
from lib.common.exceptions import RTDPConfigurationError
from lib.common.config import Config
from lib.core.init import init_logging

log = logging.getLogger('main')

pending_results = []

def data_etl(*args, **kwargs):
    handle_module = kwargs['handle_module']
    package = modules.data_etl
    prefix = package.__name__ + "."
    for _, name, _ in pkgutil.iter_modules(package.__path__, prefix):
        if name.endswith(handle_module):
            module = __import__(name, globals(), locals(), ["dummy"], 0)


    for name, value in inspect.getmembers(module):
        if inspect.isclass(value) and issubclass(value, CommonETL) and value is not CommonETL:
            log.debug("%s: %s.", name, value)
            obj = value()
            obj.save_data(**obj.fetch_data(**kwargs))

def signal_handler(signum):
    log.debug('received signal %d.', signum)

def process_job(*args, **kwargs):
    ret = pool.apply_async(data_etl, args, kwargs)
    pending_results.append(ret)

def init_task(conf):
    main_conf = conf.get('main')
    log.debug('main dp_list %s.', main_conf['dp_list'])

    for sub_dp in main_conf['dp_list'].split(','):
        log.debug('sub dp %s.', sub_dp)
        sub_dp_conf = conf.get(sub_dp)
        base_fetch_intervals = sub_dp_conf['fetch_intervals'] if 'fetch_intervals' in sub_dp_conf else None
        base_handle_module = sub_dp_conf['handle_module'] if 'handle_module' in sub_dp_conf else None
        base_at = sub_dp_conf['at'] if 'at' in sub_dp_conf else None
        for module in sub_dp_conf['module_name'].split(','):
            if module == '':
                continue
                
            log.debug('sub module %s.', module)
            module_name_conf = conf.get(module)
            if module_name_conf:
                fetch_intervals = module_name_conf['fetch_intervals'] if 'fetch_intervals' in module_name_conf else base_fetch_intervals
                at = module_name_conf['at'] if 'at' in module_name_conf else base_at
                handle_module = module_name_conf['handle_module'] if 'handle_module' in module_name_conf else base_handle_module
                log.debug('fetch_intervals: %s, at: %s, handle_module: %s.', fetch_intervals, at, handle_module)
                if at and handle_module:
                    kwargs = {'query_sql': module_name_conf['query_sql'], 'handle_module': handle_module, 'module_tag':module}
                    schedule.every().day.at(at).do(process_job, data_etl, **kwargs)
                elif fetch_intervals and handle_module:
                    kwargs = {'query_sql': module_name_conf['query_sql'], 'handle_module': handle_module, 'module_tag':module}
                    schedule.every(int(fetch_intervals)).seconds.do(process_job, data_etl, **kwargs)
                else:
                    log.error('dataprocess <%s>\'s <%s> module does not specify fetch_intervals or handle_module.', sub_dp, module)
                    raise RTDPConfigurationError('dataprocess <%s>\'s <%s> module does not specify fetch_intervals or handle_module' % (sub_dp, module))    

def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)

if __name__ == "__main__":
    init_logging(logname='realtime_forecast', log_level=logging.DEBUG)

    config = Config(file_name="dataprocess")

    init_task(config)

    pool = multiprocessing.Pool(processes=4, initializer=init_worker,
                                maxtasksperchild=1000)
    try:
        while True:
            # 迭代复制的列表
            for ar in pending_results[:]:
                if not ar.ready():
                    continue

                try:
                    ar.get()
                except Exception as exc:
                    log.critical("Exception in execute task: %s", exc)

                # 从原列表里删除
                pending_results.remove(ar)

            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt as exc:
        pool.terminate()
        raise
    finally:
        pool.join()
