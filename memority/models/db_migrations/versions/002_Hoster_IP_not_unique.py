from migrate.changeset.constraint import UniqueConstraint
from sqlalchemy import MetaData, Table, Column, Integer, String, TIMESTAMP

meta = MetaData()

host = Table(
    'hosts', meta,
    Column('id', Integer(), primary_key=True, nullable=False),
    Column('address', String(length=128), nullable=False, unique=True),
    Column('ip', String(length=15), nullable=False, unique=True),
    Column('last_ping', TIMESTAMP, nullable=True),
    Column('rating', Integer(), default=0)
)

ip_unique = UniqueConstraint('ip', table=host)
address_unique = UniqueConstraint('address', table=host)


def upgrade(migrate_engine):
    meta.bind = migrate_engine
    ip_unique.drop()
    address_unique.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    ip_unique.create()
    address_unique.create()
