# -*- coding: utf-8 -*-
from models.meta import Base

from datetime import datetime
from sqlalchemy import Column, INTEGER, UniqueConstraint
from sqlalchemy.dialects.mysql import VARCHAR, DATETIME
from sqlalchemy.types import TIMESTAMP

class DBIndexCollectionStorageRT(Base):
    __tablename__ = 'index_collection_storage_rt'

    id = Column(INTEGER, primary_key=True)
    idx_datetime = Column(DATETIME)
    idx_type = Column(VARCHAR(64))   
    idx_name = Column(VARCHAR(64))
    value = Column(VARCHAR(1024))
    load_time = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)

    __table_args__ = (
        UniqueConstraint('idx_type', 'idx_name', 'idx_datetime'),
    )

class DBIndexCollectionStorageDaily(Base):
    __tablename__ = 'index_collection_storage_daily'

    id = Column(INTEGER, primary_key=True)
    idx_datetime = Column(DATETIME)
    idx_type = Column(VARCHAR(64))   
    idx_name = Column(VARCHAR(64))
    value = Column(VARCHAR(1024))
    load_time = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)

    __table_args__ = (
        UniqueConstraint('idx_type', 'idx_name', 'idx_datetime'),
    )

class DBIndexCollectionStorageHourly(Base):
    __tablename__ = 'index_collection_storage_hourly'

    id = Column(INTEGER, primary_key=True)
    idx_datetime = Column(DATETIME)
    idx_type = Column(VARCHAR(64))   
    idx_name = Column(VARCHAR(64))
    value = Column(VARCHAR(1024))
    load_time = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)

    __table_args__ = (
        UniqueConstraint('idx_type', 'idx_name', 'idx_datetime'),
    )
