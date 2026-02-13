from database import Base
from sqlalchemy import Column, Integer, String, DateTime

class Targets(Base):
    __tablename__ = 'targets'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    url = Column(String, unique=True, nullable=False, index=True)
    status_code = Column(Integer)
    last_checked = Column(DateTime)