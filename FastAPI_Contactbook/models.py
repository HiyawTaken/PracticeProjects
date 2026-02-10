from database import Base
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

class Contact(Base):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique= True, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

