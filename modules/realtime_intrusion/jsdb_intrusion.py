import functools
import logging
import time

from lib.common.abstracts import CompetitorIntrusion
from lib.core.intrusion_handler import FineBIDBHandle

log = logging.getLogger('intrusion_data_etl')

class JSDBIntrusion(CompetitorIntrusion):
    def fetch_data(self, loop, **kwargs):
        log.debug("read database begin")
        log.debug(kwargs)
        ret = FineBIDBHandle().result_from_sql(kwargs['query_sql'])
        log.debug(ret)
        log.debug("read database end")
        kwargs.update({'result': ret})
        if not loop.is_closed():
            loop.call_soon_threadsafe(functools.partial(self.save_data, **kwargs))
            
    def save_data(self, **kwargs):
        log.debug("save database begin")
        log.debug(kwargs['result'])
        for iresult in kwargs['result']:
            FineBIDBHandle().update_index_collection_storage_rt(iresult['ds'], 'jsdb', 'intrusion', iresult['y'])
        log.debug('saving...')
        log.debug("save database end")
