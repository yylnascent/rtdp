import functools
import logging
import time

from lib.common.abstracts import CommonETL
from lib.core.intrusion_handler import FineBIDBHandle

log = logging.getLogger('intrusion_data')

class DailyETL(CommonETL):
    def __init__(self):
        self.__db_handler = FineBIDBHandle()

    def fetch_data(self, **kwargs):
        log.debug("read database begin")
        log.debug(kwargs)
        ret = self.__db_handler.result_from_sql(kwargs['query_sql'])
        log.debug("read database end")
        kwargs.update({'result': ret})
        
        return kwargs
            
    def save_data(self, **kwargs):
        log.debug("save database begin")
        log.debug(kwargs)
        module_tag = kwargs['module_tag']
        _, idx_type, idx_name = module_tag.split('_', 2)
        for iresult in kwargs['result']:
            if not iresult['ds']:
                log.debug('fetch None data')
                break
            self.__db_handler.update_index_collection_storage_hourly(iresult['ds'], idx_type, idx_name, iresult['y'])
        log.debug("save database end")
