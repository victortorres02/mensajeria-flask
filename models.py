from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(24), nullable=False, unique=True)
    email = Column(String(90), nullable=False, unique=True)
    hashed_password = Column(String(80), nullable=False)
    def __repr__(self):
        return f'<User {self.username} ({self.email})>'

