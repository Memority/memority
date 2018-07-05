import contextlib
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, TIMESTAMP, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import NoResultFound

from settings import settings
from smart_contracts import memo_db_contract
from .stats import Stats
from .utils import ManagedMixin
from ..db import Base, session


class Host(Base, ManagedMixin):
    __tablename__ = 'hosts'

    id = Column(Integer, primary_key=True)
    address = Column(String(128), nullable=False, unique=True)
    ip = Column(String(15), nullable=False, unique=False)
    last_ping = Column(TIMESTAMP, nullable=True)
    rating = Column(Integer, default=0)

    hosted_files = relationship('HosterFile', secondary='hoster_files_m2m')
    renter_files = relationship('RenterFile', secondary='renter_files_m2m')

    def __init__(self, ip, address, rating=0) -> None:
        self.address = address
        self.ip = ip
        self.rating = rating

    def __repr__(self) -> str:
        return f'Hoster | address: {self.address} | ip: {self.ip}'

    def __str__(self) -> str:
        return f'Hoster | address: {self.address} | ip: {self.ip}'

    @classmethod
    def get_or_create(cls, *, ip=None, address):
        try:
            instance = session.query(cls) \
                .filter(func.lower(cls.address) == func.lower(address)) \
                .one()
        except NoResultFound:
            if not ip:
                ip = memo_db_contract.get_host_ip(address)
            instance = cls(ip=ip, address=address)
            instance.save()
        return instance

    @classmethod
    def update_or_create(cls, ip, address):
        try:
            try:
                query = session.query(cls).filter(func.lower(cls.address) == func.lower(address))
                instance = query.one()
            except NoResultFound:
                raise cls.NotFound
            instance.ip = ip
        except cls.NotFound:
            instance = cls(ip=ip, address=address)
        instance.save()

    @classmethod
    def refresh_from_contract(cls):
        hosts = memo_db_contract.get_hosts()
        for host_address in hosts:
            with contextlib.suppress(IntegrityError):
                cls.update_or_create(
                    ip=memo_db_contract.get_host_ip(host_address),
                    address=host_address
                )

    @classmethod
    def get_n(cls, n=10):
        time = Stats.get_host_list_sync_time()
        if not time or time < datetime.utcnow() - timedelta(days=settings.host_list_obsolescence_days):
            cls.refresh_from_contract()
            Stats.update_host_list_sync_time()
        return session.query(cls).filter(cls.address != settings.address).order_by(func.random()).limit(n)

    @classmethod
    def get_queryset_for_uploading_file(cls, file):
        res = session.query(Host) \
            .filter(~func.lower(cls.address).in_([h.address.lower() for h in file.hosts])) \
            .order_by(func.random()) \
            .all()
        if not res:
            cls.refresh_from_contract()
            res = session.query(Host) \
                .filter(~func.lower(cls.address).in_([h.address.lower() for h in file.hosts])) \
                .order_by(func.random()) \
                .all()
        return res
