from sqlalchemy import *

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine
    hoster_files = Table('hoster_files', meta, autoload=True)
    hoster_files.c.client_contract_address.alter(name='client_address')


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    hoster_files = Table('hoster_files', meta, autoload=True)
    hoster_files.c.client_address.alter(name='client_contract_address')
