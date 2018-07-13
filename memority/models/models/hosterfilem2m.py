from datetime import datetime
from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.exc import NoResultFound

from .host import Host
from .hosterfile import HosterFile
from .utils import ManagedMixin
from ..db import Base, session


class HosterFileM2M(Base, ManagedMixin):
    INIT, ACTIVE, OFFLINE, SYNC, REMOVED = 'init', 'active', 'offline', 'sync', 'removed'

    __tablename__ = 'hoster_files_m2m'

    file_id = Column(Integer, ForeignKey('hoster_files.id'), primary_key=True)
    host_id = Column(Integer, ForeignKey('hosts.id'), primary_key=True)
    time = Column(TIMESTAMP, default=datetime.utcnow)
    last_ping = Column(TIMESTAMP, nullable=True)
    status = Column(String(32), default=ACTIVE)
    offline_counter = Column(Integer, default=0)

    file = relationship(HosterFile, backref=backref("hoster_files_assoc"))
    host = relationship(Host, backref=backref("hf_hosts_assoc"))

    def __repr__(self) -> str:
        return f'HosterFileM2M <file: {self.file} || {self.host}>'

    def __str__(self) -> str:
        return f'HosterFileM2M <file: {self.file} || {self.host}>'

    def update_last_ping(self):
        self.last_ping = datetime.utcnow()
        self.save()

    def update_offline_counter(self):
        self.offline_counter += 1
        self.save()

    def reset_offline_counter(self):
        self.offline_counter = 0
        self.save()

    def update_status(self, status):
        self.status = status
        self.save()

    @classmethod
    def get_status(cls, file_hash, host_address):
        try:
            return session.query(cls.status) \
                .join(cls.file) \
                .filter_by(hash=file_hash) \
                .join(cls.host) \
                .filter_by(address=host_address) \
                .one()[0]
        except NoResultFound:
            raise cls.NotFound
