from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref

from .host import Host
from .renterfile import RenterFile
from .utils import ManagedMixin
from ..db import Base


class RenterFileM2M(Base, ManagedMixin):
    __tablename__ = 'renter_files_m2m'

    file_id = Column(Integer, ForeignKey('renter_files.id'), primary_key=True)
    host_id = Column(Integer, ForeignKey('hosts.id'), primary_key=True)

    file = relationship(RenterFile, backref=backref("renter_files_assoc"))
    host = relationship(Host, backref=backref("rf_hosts_assoc"))
