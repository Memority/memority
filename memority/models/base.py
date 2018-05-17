import contextlib
import os
from datetime import datetime, timedelta
from io import BytesIO

import aiofiles
import tzlocal
from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, func, Boolean
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.exc import NoResultFound

from settings import settings
from smart_contracts import token_contract, client_contract, memo_db_contract, ClientContract
from utils import compute_hash, InvalidSignature, encrypt, decrypt, sign, DecryptionError
from .db import Base, session


class Manager:

    def __init__(self, managed_class) -> None:
        super().__init__()
        self._managed_class = managed_class

    def all(self):
        return session.query(self._managed_class).all()

    def get(self, **kwargs):
        try:
            query = session.query(self._managed_class).filter_by(**kwargs)
            return query.one()
        except NoResultFound:
            raise self._managed_class.NotFound


class ManagedMixin:

    def __init_subclass__(cls, **kwargs):
        cls.NotFound = type('NotFound', (Exception,), {})
        cls.AlreadyExists = type('AlreadyExists', (Exception,), {})
        cls.MultipleObjectsReturned = type('MultipleObjectsReturned', (Exception,), {})
        cls.objects = Manager(cls)

    def save(self):
        try:
            session.add(self)
            session.commit()
        except IntegrityError:
            session.rollback()
            raise

    def delete(self):
        with contextlib.suppress(InvalidRequestError):
            session.delete(self)
            session.commit()


class Host(Base, ManagedMixin):
    __tablename__ = 'hosts'

    id = Column(Integer, primary_key=True)
    address = Column(String(128), nullable=False, unique=True)
    ip = Column(String(15), nullable=False, unique=True)
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
    def get_one_for_uploading_file(cls, file):
        res = session.query(Host) \
            .filter(~cls.address.in_([h.address for h in file.hosts])) \
            .order_by(func.random()) \
            .first()
        if not res:
            cls.refresh_from_contract()
            res = session.query(Host) \
                .filter(~cls.address.in_([h.address for h in file.hosts])) \
                .order_by(func.random()) \
                .first()
        return res


class HosterFile(Base, ManagedMixin):
    __tablename__ = 'hoster_files'
    ACTIVE, WAIT_DEL = 'active', 'wait_del'

    id = Column(Integer, primary_key=True)
    hash = Column(String(64), nullable=False, unique=True)
    owner_key = Column(String(128), nullable=False)
    signature = Column(String(128), nullable=True)
    path = Column(String(512), nullable=True)
    timestamp = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    size = Column(Integer, nullable=True)
    client_contract_address = Column(String(128), nullable=False)
    my_monitoring_number = Column(Integer, default=0)
    status = Column(String(32), nullable=False, default=ACTIVE)
    no_deposit_counter = Column(Integer, default=0)
    replacing_host_address = Column(String(128), nullable=True)
    send_data_to_contract_after_uploading_body = Column(Boolean, default=False)
    hosts = relationship(
        'Host',
        secondary='hoster_files_m2m'
    )

    def __init__(self, hash_, owner_key, signature, client_contract_address, size=None) -> None:
        self.hash = hash_
        self.owner_key = owner_key
        self.signature = signature
        self.client_contract_address = client_contract_address
        if size:
            self.size = size

    def __repr__(self) -> str:
        return self.hash

    def __str__(self) -> str:
        return self.hash

    @property
    def client_contract(self):
        return ClientContract(address=self.client_contract_address)

    @classmethod
    async def create_metadata(cls, file_hash, owner_key, signature, client_contract_address, size,
                              hosts=None, replacing=None):
        # ToDo: size limit based on space available
        if len(signature) != 128:
            raise InvalidSignature
        try:
            instance = cls(
                hash_=file_hash,
                owner_key=owner_key,
                signature=signature,
                client_contract_address=client_contract_address,
                size=size
            )
            instance.save()
            if hosts:
                if replacing:
                    index = hosts.index(replacing)
                    hosts[index] = settings.address  # for properly setting monitoring num
                else:
                    hosts.append(settings.address)
                instance.add_hosts(hosts)
                instance.send_data_to_contract_after_uploading_body = True
                if replacing:
                    instance.replacing_host_address = replacing
                instance.save()
        except IntegrityError:
            session.rollback()
            raise cls.AlreadyExists
        return instance

    @classmethod
    async def load_body(cls, data_reader, file_hash):
        instance = cls.find(file_hash)
        # ToDo: verify signature

        path = os.path.join(settings.boxes_dir, file_hash)
        async with aiofiles.open(path, 'wb') as f:
            async for chunk, _ in data_reader:
                await f.write(chunk)

        instance.path = path

        instance.save()
        if instance.send_data_to_contract_after_uploading_body:
            if instance.replacing_host_address:
                await instance.client_contract.replace_host(
                    file_hash,
                    old_host_address=instance.replacing_host_address
                )
            else:
                await instance.client_contract.add_host_to_file(
                    file_hash
                )
        return instance

    def delete(self):
        with contextlib.suppress(FileNotFoundError):
            os.remove(os.path.join(settings.boxes_dir, self.hash))
        for hf in self.file_hosts:
            hf.delete()
        super().delete()

    async def get_body(self):
        path = os.path.join(settings.boxes_dir, self.hash)
        try:
            async with aiofiles.open(path, 'rb') as f:
                body = await f.read()
            return body
        except FileNotFoundError:
            raise self.NotFound

    async def get_filelike(self):
        path = os.path.join(settings.boxes_dir, self.hash)
        try:
            async with aiofiles.open(path, 'rb') as f:
                chunk = await f.read(64 * 1024)
                while chunk:
                    yield chunk
                    chunk = await f.read(64 * 1024)
        except FileNotFoundError:
            raise self.NotFound

    @property
    def body_exists(self):
        return os.path.isfile(os.path.join(settings.boxes_dir, self.hash))

    async def compute_chunk_hash(self, from_: int, to_: int) -> str:
        body = await self.get_body()
        chunk = body[from_:to_]
        return compute_hash(chunk)

    @classmethod
    def find(cls, box_hash):
        try:
            instance = cls.objects.get(hash=box_hash)
            return instance
        except NoResultFound:
            raise cls.NotFound

    @classmethod
    def list_hashes(cls):
        results = session.query(cls.hash).all()
        return results

    def add_hosts(self, hosts: list):
        # client_contract file hosts - sequential, so it is ok.
        with contextlib.suppress(ValueError):
            my_num = [h.lower() for h in hosts].index(settings.address.lower())
            self.my_monitoring_number = my_num
        for host_address in hosts:
            host = Host.get_or_create(address=host_address)
            if host not in self.hosts:
                self.hosts.append(host)
        self.save()

    @property
    def file_hosts(self):
        return session.query(HosterFileM2M).join(HosterFile).filter(HosterFile.id == self.id).all()

    @classmethod
    def refresh_from_contract(cls):
        for file in cls.objects.all():
            file_hosts_db = file.file_hosts
            file_hosts_contract = file.client_contract.get_file_hosts(file.hash)
            # region Delete from db file hosts, removed from contract.
            for hfm2m in [h for h in file_hosts_db if h.host.address not in file_hosts_contract]:
                hfm2m.delete()
            # endregion
            file.add_hosts(
                file_hosts_contract
            )

    def update_no_deposit_counter(self):
        self.no_deposit_counter += 1
        self.save()

    def reset_no_deposit_counter(self):
        self.no_deposit_counter = 0
        self.save()

    def update_status(self, status):
        self.status = status
        self.save()

    async def check_deposit(self):
        return await token_contract.get_deposit(
            file_hash=self.hash,
            owner_contract_address=self.client_contract_address
        )

    @classmethod
    def get_total_size(cls):
        return session.query(func.sum(cls.size)).one()[0] or 0


class RenterFile(Base, ManagedMixin):
    __tablename__ = 'renter_files'
    PREPARING, UPLOADING, UPLOADED = 'preparing', 'uploading', 'uploaded'

    id = Column(Integer, primary_key=True)
    hash = Column(String(64), nullable=True, unique=True)
    signature = Column(String(128), nullable=True)
    name = Column(String(256), nullable=True)
    timestamp = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    status = Column(String(32), nullable=False, default=PREPARING)
    hosters = relationship(
        'Host',
        secondary='renter_files_m2m'
    )

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name

    def __init__(self, *, name, body=None, hash_=None, encrypted=False, status=None) -> None:
        self.name = name
        self.body = body
        self.encrypted = encrypted
        self.hash = hash_
        self.status = status or self.PREPARING

    def get_filelike(self):
        return BytesIO(self.body)

    @classmethod
    async def open(cls, path):
        async with aiofiles.open(path, 'rb') as f:
            body = await f.read()
        return cls(
            name=os.path.basename(path),
            body=body,
            hash_=compute_hash(body + settings.address.encode('utf-8'))
        )

    @classmethod
    async def list(cls):
        results = session.query(cls).all()
        return [await r.to_json() for r in results]

    @classmethod
    def find(cls, hash_):
        try:
            instance = cls.objects.get(hash=hash_)
            return instance
        except NoResultFound:
            cls.refresh_from_contract()
            try:
                instance = cls.objects.get(hash=hash_)
                return instance
            except NoResultFound:
                raise cls.NotFound

    @classmethod
    def update_or_create(cls, name, hash_, hosts, status=None):
        try:
            instance = cls.objects.get(hash=hash_)
            instance.name = name
        except cls.NotFound:
            instance = cls(name=name, hash_=hash_, encrypted=True, status=status)

        for host_address in hosts:
            host = Host.get_or_create(address=host_address)
            instance.hosters.append(host)

        instance.save()

    def load_body(self, body: bytes):
        self.body = body
        self.encrypted = True

    async def save_to_fs(self, destination=None):
        assert not self.encrypted
        path = os.path.join(destination, self.name) if destination else self.name
        if os.path.isfile(path):
            raise FileExistsError
        async with aiofiles.open(path, 'wb') as f:
            await f.write(self.body)

    @property
    def file_hosts(self):
        return session.query(RenterFileM2M).join(RenterFile).filter(RenterFile.id == self.id).all()

    def delete(self):
        for h in self.file_hosts:
            h.delete()
        super().delete()

    def encrypt(self):
        self.body = encrypt(self.body)
        self.name = encrypt(self.name.encode('utf-8')).decode('utf-8')
        self.encrypted = True

    def decrypt(self):
        self.body = decrypt(self.body)
        with contextlib.suppress(DecryptionError):
            self.name = decrypt(
                self.name.encode('utf-8') if isinstance(self.name, bytes) else self.name.encode('utf-8')
            ).decode('utf-8')
        self.encrypted = False

    def sign(self):
        self.signature = sign(self.body)

    def prepare_to_uploading(self):
        self.encrypt()
        self.sign()
        self.save()

    def update_status(self, status):
        self.status = status
        with contextlib.suppress(IntegrityError):
            self.save()

    @property
    def size(self):
        return len(self.body)

    def add_hosters(self, hosters):
        for host in hosters:
            self.hosters.append(host)
        self.save()

    @classmethod
    def refresh_from_contract(cls):
        with contextlib.suppress(AttributeError):
            files = client_contract.get_files()
            for file_hash in files:
                cls.update_or_create(
                    name=client_contract.get_file_name(file_hash),
                    hash_=file_hash,
                    hosts=client_contract.get_file_hosts(file_hash),
                    status=cls.UPLOADED
                )
            for file in cls.objects.all():
                if file.hash not in files:
                    file.delete()

    async def to_json(self):
        res = {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}
        try:
            name = decrypt(
                self.name.encode('utf-8') if isinstance(self.name, bytes) else self.name.encode('utf-8')
            ).decode('utf-8')
        except DecryptionError:
            name = self.name
        res['name'] = name
        res['timestamp'] = self.timestamp.astimezone(tzlocal.get_localzone()).strftime('%Y-%m-%d %H:%M') + ' UTC'
        try:
            res['deposit_ends_on'] = (
                                             datetime.now() +
                                             timedelta(
                                                 hours=(
                                                         await token_contract.get_deposit(file_hash=self.hash) /
                                                         (
                                                                 token_contract.tokens_per_byte_hour *
                                                                 client_contract.get_file_size(self.hash) *
                                                                 10  # hosters per file
                                                         )
                                                 )
                                             )
                                     ).strftime('%Y-%m-%d %H:%M') + ' UTC'
        except OverflowError:
            res['deposit_ends_on'] = datetime.max.strftime('%Y-%m-%d %H:%M') + ' UTC'
        return res


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


class RenterFileM2M(Base, ManagedMixin):
    __tablename__ = 'renter_files_m2m'
    file_id = Column(Integer, ForeignKey('renter_files.id'), primary_key=True)
    host_id = Column(Integer, ForeignKey('hosts.id'), primary_key=True)
    file = relationship(RenterFile, backref=backref("renter_files_assoc"))
    host = relationship(Host, backref=backref("rf_hosts_assoc"))


class Wallet(Base, ManagedMixin):
    __tablename__ = 'wallets'

    id = Column(Integer, primary_key=True)
    address = Column(String(64), nullable=False)
    balance = Column(Integer, default=0)


class Stats(Base, ManagedMixin):
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
