import functools
import logging
import time

from lib.common.abstracts import CompetitorIntrusion
from lib.core.intrusion_handler import FineBIDBHandle

log = logging.getLogger('intrusion_data')

class CommonCompetitorIntrusion(CompetitorIntrusion):
    def fetch_data(self, **kwargs):
        log.debug("read database begin")
        log.debug(kwargs)
        ret = FineBIDBHandle().result_from_sql(kwargs['query_sql'])
        log.debug("read database end")
        kwargs.update({'result': ret})
        
        return kwargs
            
    def save_data(self, **kwargs):
        log.debug("save database begin")
        log.debug(kwargs)
        module_tag = kwargs['module_tag']
        idx_type, idx_name = module_tag.split('_', 1)
        for iresult in kwargs['result']:
            FineBIDBHandle().update_index_collection_storage_rt(iresult['ds'], idx_type, idx_name, iresult['y'])
        log.debug("save database end")
