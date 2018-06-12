# -*- coding: utf-8 -*-
"""
   FineBI Database Handler
"""

import logging
import transaction

from sqlalchemy.exc import SQLAlchemyError

from lib.common.config import Config
from lib.common.db_conn_util import get_engine, get_session_factory, get_tm_session
from models.meta import Base

# import or define all models here to ensure they are attached to the
# Base.metadata prior to any initialization routines
from models.incursion_model import DBIndexCollectionStorageRT, \
    DBIndexCollectionStorageDaily, DBIndexCollectionStorageHourly

log = logging.getLogger('finebi_db_handle')


class FineBIDBHandle(object):
    
    def __init__(self):
        self.__transaction_manager = transaction.manager
        self.init_db()
    
    def __del__(self):
        self.__transaction_manager.commit()
    
    def init_db(self):
        config = Config(file_name="finebi-database")
        self.engine = get_engine({'sqlalchemy.url': config.get('database')['sqlalchemy.url']})

        self.session = get_tm_session(get_session_factory(self.engine), self.__transaction_manager)

        Base.metadata.bind = self.engine
        Base.metadata.create_all(self.engine)

    def result_from_sql(self, query_sql):
        ret = None
        if query_sql:
            ret = self.session.execute(query_sql).fetchall()

        return ret

    def __update_index_table(self, model_name, idx_datetime, idx_type, idx_name, value):
        # overwrite it if existed, otherwise insert one.
        ret = self.session.query(model_name).\
              filter(model_name.idx_datetime==idx_datetime).\
              filter(model_name.idx_type==idx_type).\
              filter(model_name.idx_name==idx_name).\
              first()

        if not ret:
            ret = model_name()
            ret.idx_datetime = idx_datetime
            ret.idx_type = idx_type
            ret.idx_name = idx_name
            ret.value = value
            self.session.add(ret)
        else:
            ret.value = value

        try:
            self.session.flush()
            log.debug('__update_index_table success.')
            return True
        except SQLAlchemyError as exc:
            log.error('__update_index_table fail, error msg: %s', exc)
            return False

    def update_index_collection_storage_rt(self, idx_datetime, idx_type, idx_name, value):
        return self.__update_index_table(DBIndexCollectionStorageRT, idx_datetime, idx_type, idx_name, value)

    def update_index_collection_storage_daily(self, idx_datetime, idx_type, idx_name, value):
        return self.__update_index_table(DBIndexCollectionStorageDaily, idx_datetime, idx_type, idx_name, value)

    def update_index_collection_storage_hourly(self, idx_datetime, idx_type, idx_name, value):
        return self.__update_index_table(DBIndexCollectionStorageHourly, idx_datetime, idx_type, idx_name, value)
