import logging
import os
from migrate import DatabaseNotControlledError
from migrate.versioning.api import db_version, version, version_control, script, test, upgrade

from settings import settings

logger = logging.getLogger('memority')


class DBManager:

    def __init__(self) -> None:
        self.db_url = f'sqlite:///{settings.db_path}'
        self.repository = settings.db_migrations_path

    def add_db(self, version_=None):
        return version_control(
            url=self.db_url,
            repository=self.repository,
            version=version_
        )

    @property
    def db_version(self):
        return db_version(
            url=self.db_url,
            repository=self.repository,
        )

    @property
    def repo_version(self):
        return version(
            repository=self.repository,
        )

    def new_script(self, name: str):
        return script(
            description=name,
            repository=self.repository
        )

    def test(self):
        return test(
            url=self.db_url,
            repository=self.repository,
        )

    def upgrade(self):
        return upgrade(
            url=self.db_url,
            repository=self.repository,
        )

    def ensure_db_up_to_date(self):
        if not os.path.isfile(settings.db_path):
            logger.info(f'Creating DB at {settings.db_path}')
            self.add_db()
        else:
            try:
                logger.info(f'DB version: v{self.db_version}')
            except DatabaseNotControlledError:
                self.add_db(version_=1)
        if self.db_version != self.repo_version:
            logger.info(f'Upgrading DB to v{self.repo_version}')
            self.upgrade()


db_manager = DBManager()

if __name__ == '__main__':
    db_manager.ensure_db_up_to_date()
