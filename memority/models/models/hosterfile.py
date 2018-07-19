import aiofiles
import contextlib
import os
from datetime import datetime
from sqlalchemy import Column, Integer, String, TIMESTAMP, func, Boolean
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import NoResultFound

from bugtracking import raven_client
from settings import settings
from smart_contracts import token_contract, memo_db_contract, ClientContract
from utils import compute_hash, InvalidSignature
from .host import Host
from .utils import ManagedMixin
from ..db import Base, session


class HosterFile(Base, ManagedMixin):
    ACTIVE, WAIT_DEL = 'active', 'wait_del'

    __tablename__ = 'hoster_files'

    id = Column(Integer, primary_key=True)
    hash = Column(String(64), nullable=False, unique=True)
    owner_key = Column(String(128), nullable=False)
    signature = Column(String(128), nullable=True)
    path = Column(String(512), nullable=True)
    timestamp = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    size = Column(Integer, nullable=True)
    client_address = Column(String(128), nullable=False)
    my_monitoring_number = Column(Integer, default=0)
    status = Column(String(32), nullable=False, default=ACTIVE)
    no_deposit_counter = Column(Integer, default=0)
    replacing_host_address = Column(String(128), nullable=True)
    send_data_to_contract_after_uploading_body = Column(Boolean, default=False)

    hosts = relationship('Host', secondary='hoster_files_m2m')

    def __init__(self, hash_, owner_key, signature, client_address, size=None) -> None:
        self.hash = hash_
        self.owner_key = owner_key
        self.signature = signature
        self.client_address = client_address
        if size:
            self.size = size

    def __repr__(self) -> str:
        return self.hash

    def __str__(self) -> str:
        return self.hash

    @property
    def client_contract(self):
        client_contract_address = memo_db_contract.get_client_contract_address(owner=self.client_address)
        return ClientContract(address=client_contract_address)

    @classmethod
    async def create_metadata(cls, file_hash, owner_key, signature, client_address, size,
                              hosts=None, replacing=None):
        if len(signature) != 128:
            raise InvalidSignature
        try:
            instance = cls(
                hash_=file_hash,
                owner_key=owner_key,
                signature=signature,
                client_address=client_address,
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
            raven_client.captureException()
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
        if settings.address.lower() not in \
                [h.lower() for h in instance.client_contract.get_file_hosts(instance.hash)]:
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
        from .hosterfilem2m import HosterFileM2M
        return session.query(HosterFileM2M).join(HosterFile).filter(HosterFile.id == self.id).all()

    @property
    def contract_file_hosts(self):
        return self.client_contract.get_file_hosts(self.hash)

    @classmethod
    def refresh_from_contract(cls):
        for file in cls.objects.all():
            file: HosterFile
            file_hosts_db = file.file_hosts
            contract_file_hosts = file.contract_file_hosts
            # region Delete from db file hosts, removed from contract.
            for hfm2m in [h for h in file_hosts_db if h.host.address not in contract_file_hosts]:
                hfm2m.delete()
            # endregion
            file.add_hosts(
                contract_file_hosts
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
            owner_address=self.client_address
        )

    @classmethod
    def get_total_size(cls):
        return session.query(func.sum(cls.size)).one()[0] or 0
