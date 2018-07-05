import aiofiles
import contextlib
import os
import tzlocal
from datetime import datetime, timedelta
from io import BytesIO
from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import NoResultFound

from settings import settings
from smart_contracts import token_contract, client_contract
from utils import compute_hash, encrypt, decrypt, sign, DecryptionError
from .host import Host
from .utils import ManagedMixin
from ..db import Base, session


class RenterFile(Base, ManagedMixin):
    PREPARING, UPLOADING, UPLOADED = 'preparing', 'uploading', 'uploaded'

    __tablename__ = 'renter_files'

    id = Column(Integer, primary_key=True)
    hash = Column(String(64), nullable=True, unique=True)
    signature = Column(String(128), nullable=True)
    name = Column(String(256), nullable=True)
    timestamp = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    status = Column(String(32), nullable=False, default=PREPARING)

    hosters = relationship('Host', secondary='renter_files_m2m')

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
        from .renterfilem2m import RenterFileM2M
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
        res['size'] = client_contract.get_file_size(self.hash)
        res['price_per_hour'] = token_contract.wmmr_to_mmr(token_contract.tokens_per_byte_hour * res['size'] * 10)
        res['timestamp'] = self.timestamp.astimezone(tzlocal.get_localzone()).strftime('%Y-%m-%d %H:%M') + ' UTC'
        try:
            res['deposit_ends_on'] = (
                    (
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
                    ).strftime('%Y-%m-%d %H:%M')
                    + ' UTC'
            )
        except OverflowError:
            res['deposit_ends_on'] = datetime.max.strftime('%Y-%m-%d %H:%M') + ' UTC'
        return res
