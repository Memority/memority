from datetime import datetime

from sqlalchemy import *

meta = MetaData()

hoster_file_old = Table(
    'hoster_files', meta,
    Column('id', Integer(), primary_key=True, nullable=False),
    Column('hash', String(length=64), nullable=False, unique=True),
    Column('owner_key', String(length=128), nullable=False),
    Column('signature', String(length=128), nullable=True),
    Column('path', String(length=512), nullable=True),
    Column('timestamp', TIMESTAMP, nullable=False, default=datetime.utcnow),
    Column('size', Integer()),
    Column('client_contract_address', String(length=128), nullable=False),
    Column('my_monitoring_number', Integer(), default=ColumnDefault(0)),
    Column('status', String(length=32), nullable=False, default=ColumnDefault('active')),
    Column('no_deposit_counter', Integer(), default=ColumnDefault(0)),
    Column('replacing_host_address', String(length=128)),
    Column('send_data_to_contract_after_uploading_body', Boolean(), default=ColumnDefault(False)),
)

hoster_file_new = Table(
    'hoster_files', meta,
    Column('id', Integer(), primary_key=True, nullable=False),
    Column('hash', String(length=64), nullable=False, unique=True),
    Column('owner_key', String(length=128), nullable=False),
    Column('signature', String(length=128), nullable=True),
    Column('path', String(length=512), nullable=True),
    Column('timestamp', TIMESTAMP, nullable=False, default=datetime.utcnow),
    Column('size', Integer()),
    Column('client_address', String(length=128), nullable=False),
    Column('my_monitoring_number', Integer(), default=ColumnDefault(0)),
    Column('status', String(length=32), nullable=False, default=ColumnDefault('active')),
    Column('no_deposit_counter', Integer(), default=ColumnDefault(0)),
    Column('replacing_host_address', String(length=128)),
    Column('send_data_to_contract_after_uploading_body', Boolean(), default=ColumnDefault(False)),
)


def upgrade(migrate_engine):
    meta.bind = migrate_engine
    hoster_file_old.c.client_contract_address.alter(name='client_address')


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    hoster_file_new.c.client_address.alter(name='client_contract_address')
