from datetime import datetime
from sqlalchemy import Column, Integer, TIMESTAMP
from sqlalchemy.orm.exc import NoResultFound

from .utils import ManagedMixin
from ..db import Base, session


class Stats(Base, ManagedMixin):  # ToDo: rm class, mv data to settings
    __tablename__ = 'stats'

    id = Column(Integer, primary_key=True)
    host_list_sync_time = Column(TIMESTAMP, nullable=True)

    @classmethod
    def load(cls):
        try:
            instance = session.query(cls).one()
            return instance
        except NoResultFound:
            instance = cls()
            instance.save()
            return instance

    @classmethod
    def get_host_list_sync_time(cls):
        return cls.load().host_list_sync_time

    @classmethod
    def update_host_list_sync_time(cls):
        instance = cls.load()
        instance.host_list_sync_time = datetime.utcnow()
        instance.save()
