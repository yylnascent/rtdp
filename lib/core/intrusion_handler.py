 # -*- coding: utf-8 -*-
import transaction
import time
import logging

from sqlalchemy.exc import SQLAlchemyError, IntegrityError


from lib.common.config import Config
from lib.common.db_conn_util import get_engine, get_session_factory, get_tm_session
from models.meta import Base

# import or define all models here to ensure they are attached to the
# Base.metadata prior to any initialization routines
from models.incursion_model import DBIndexCollectionStorageRT, DBIndexCollectionStorageDaily, DBIndexCollectionStorageHourly

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

    def update_index_collection_storage_rt(self, idx_datetime, idx_type, idx_name, value):
        # overwrite it if existed, otherwise insert one.
        ret = self.session.query(DBIndexCollectionStorageRT).\
              filter(DBIndexCollectionStorageRT.idx_datetime==idx_datetime).\
              filter(DBIndexCollectionStorageRT.idx_type==idx_type).\
              filter(DBIndexCollectionStorageRT.idx_name==idx_name).\
              first()

        if not ret:
            ret = DBIndexCollectionStorageRT()
            ret.idx_datetime = idx_datetime
            ret.idx_type = idx_type
            ret.idx_name = idx_name
            ret.value = value
            self.session.add(ret)
        else:
            ret.value = value

        try:
            self.session.flush()
            log.debug('update_index_collection_storage_rt success.')
            return True
        except SQLAlchemyError as exc:
            log.error('update_index_collection_storage_rt fail, error msg: {}'.format(exc))
            return False

    def update_index_collection_storage_daily(self, idx_datetime, idx_type, idx_name, value):
        # overwrite it if existed, otherwise insert one.
        ret = self.session.query(DBIndexCollectionStorageDaily).\
              filter(DBIndexCollectionStorageDaily.idx_datetime==idx_datetime).\
              filter(DBIndexCollectionStorageDaily.idx_type==idx_type).\
              filter(DBIndexCollectionStorageDaily.idx_name==idx_name).\
              first()

        if not ret:
            ret = DBIndexCollectionStorageDaily()
            ret.idx_datetime = idx_datetime
            ret.idx_type = idx_type
            ret.idx_name = idx_name
            ret.value = value
            self.session.add(ret)
        else:
            ret.value = value

        try:
            self.session.flush()
            log.debug('update_index_collection_storage_daily success.')
            return True
        except SQLAlchemyError as exc:
            log.error('update_index_collection_storage_daily fail, error msg: {}'.format(exc))
            return False

    def update_index_collection_storage_hourly(self, idx_datetime, idx_type, idx_name, value):
        # overwrite it if existed, otherwise insert one.
        ret = self.session.query(DBIndexCollectionStorageHourly).\
              filter(DBIndexCollectionStorageHourly.idx_datetime==idx_datetime).\
              filter(DBIndexCollectionStorageHourly.idx_type==idx_type).\
              filter(DBIndexCollectionStorageHourly.idx_name==idx_name).\
              first()

        if not ret:
            ret = DBIndexCollectionStorageHourly()
            ret.idx_datetime = idx_datetime
            ret.idx_type = idx_type
            ret.idx_name = idx_name
            ret.value = value
            self.session.add(ret)
        else:
            ret.value = value

        try:
            self.session.flush()
            log.debug('update_index_collection_storage_hourly success.')
            return True
        except SQLAlchemyError as exc:
            log.error('update_index_collection_storage_hourly fail, error msg: {}'.format(exc))
            return False

