# -*- coding: utf-8 -*-
from models.meta import Base

from sqlalchemy import Column
from sqlalchemy import INTEGER
from sqlalchemy.dialects.mssql import VARCHAR
from sqlalchemy.types import TIMESTAMP

class DBSafeRealtimeIntrusion(Base):
    __tablename__ = 'rt_safe_realtime_incursion'

    id = Column(INTEGER, primary_key=True)
    type = Column(VARCHAR(64))   
    name = Column(VARCHAR(64))
    value = Column(INTEGER)
    server_time = Column(TIMESTAMP)
    update_time = Column(TIMESTAMP)
