from datetime import datetime

from sqlalchemy import Table, Column, Integer, String, MetaData, TIMESTAMP, ColumnDefault, Boolean, ForeignKey

meta = MetaData()

host = Table(
    'hosts', meta,
    Column('id', Integer(), primary_key=True, nullable=False),
    Column('address', String(length=128), nullable=False, unique=True),
    Column('ip', String(length=15), nullable=False, unique=True),
    Column('last_ping', TIMESTAMP, nullable=True),
    Column('rating', Integer(), default=0)
)

hoster_file = Table(
    'hoster_files', meta,
    Column('id', Integer(), primary_key=True, nullable=False),
    Column('hash', String(length=64), nullable=False, unique=True),
    Column('owner_key', String(length=128), nullable=False),
    Column('signature', String(length=128), nullable=True),
    Column('path', String(length=512), nullable=True),
    Column('timestamp', TIMESTAMP, nullable=False, default=datetime.utcnow),
    Column('size', Integer()), Column('client_contract_address', String(length=128), nullable=False),
    Column('my_monitoring_number', Integer(), default=ColumnDefault(0)),
    Column('status', String(length=32), nullable=False, default=ColumnDefault('active')),
    Column('no_deposit_counter', Integer(), default=ColumnDefault(0)),
    Column('replacing_host_address', String(length=128)),
    Column('send_data_to_contract_after_uploading_body', Boolean(), default=ColumnDefault(False)),

)

hoster_file_m2m = Table(
    'hoster_files_m2m', meta,
    Column('file_id', Integer(), ForeignKey('hoster_files.id'), primary_key=True, nullable=False),
    Column('host_id', Integer(), ForeignKey('hosts.id'), primary_key=True, nullable=False),
    Column('time', TIMESTAMP(), default=datetime.utcnow), Column('last_ping', TIMESTAMP()),
    Column('status', String(length=32), default=ColumnDefault('active')),
    Column('offline_counter', Integer(), default=ColumnDefault(0)),
)

renter_file = Table(
    'renter_files', meta,
    Column('id', Integer(), primary_key=True, nullable=False),
    Column('hash', String(length=64)), Column('signature', String(length=128)),
    Column('name', String(length=256)),
    Column('timestamp', TIMESTAMP(), nullable=False, default=datetime.utcnow),
    Column('status', String(length=32), nullable=False, default=ColumnDefault('preparing')),

)

renter_file_m2m = Table(
    'renter_files_m2m', meta,
    Column('file_id', Integer(), ForeignKey('renter_files.id'), primary_key=True, nullable=False),
    Column('host_id', Integer(), ForeignKey('hosts.id'), primary_key=True, nullable=False),

)

stats = Table(
    'stats', meta,
    Column('id', Integer(), primary_key=True, nullable=False),
    Column('host_list_sync_time', TIMESTAMP()),
)


def upgrade(migrate_engine):
    meta.bind = migrate_engine
    host.create()
    hoster_file.create()
    hoster_file_m2m.create()
    renter_file.create()
    renter_file_m2m.create()
    stats.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    host.drop()
    hoster_file.drop()
    hoster_file_m2m.drop()
    renter_file.drop()
    renter_file_m2m.drop()
    stats.drop()
