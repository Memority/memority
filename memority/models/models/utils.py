import contextlib
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.orm.exc import NoResultFound

from ..db import session


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
