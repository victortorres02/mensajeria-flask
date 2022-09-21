from sqlalchemy import Column, ForeignKey, Integer, String, TIMESTAMP
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(24), nullable=False, unique=True)
    email = Column(String(90), nullable=False, unique=True)
    hashed_password = Column(String(127), nullable=False)
    sessions = relationship(
            'SessionId', back_populates='user')
    def __repr__(self):
        return f'<User {self.username} ({self.email})>'

class SessionId(Base):
    __tablename__ = 'session_ids'
    token = Column(String(64), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    creation_time = Column(TIMESTAMP, nullable=False)
    last_use_time = Column(TIMESTAMP, nullable=False)
    user = relationship (
            'User', back_populates='sessions')

class InvalidCredentialsError(Exception):
    pass

