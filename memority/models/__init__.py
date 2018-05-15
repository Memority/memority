from .base import Wallet, Stats, HosterFile, Host, RenterFile, RenterFileM2M, HosterFileM2M
from .db import engine, create_tables

if not all(
        [
            engine.dialect.has_table(
                engine.connect(),
                table_name=cls.__tablename__
            )
            for cls in [RenterFile, Host, HosterFile, Wallet, Stats, RenterFileM2M, HosterFileM2M]
        ]):
    create_tables()
