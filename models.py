from sqlalchemy import Table, Column, ForeignKey, Integer, String, TIMESTAMP, LargeBinary
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(24), nullable=False, unique=True)
    email = Column(String(90), nullable=False, unique=True)
    hashed_password = Column(String(127), nullable=False)
    sessions = relationship(
            'SessionId', back_populates='user', cascade='all, delete-orphan')
    chats = relationship(
            'UserChat', secondary='user_chat_membership', back_populates='members')
    def __repr__(self):
        return f'<User {self.username} ({self.email})>'

class SessionId(Base):
    __tablename__ = 'session_ids'
    token = Column(String(64), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    creation_time = Column(TIMESTAMP, nullable=False)
    last_use_time = Column(TIMESTAMP, nullable=False)
    expire_time   = Column(TIMESTAMP, nullable=False)
    user = relationship (
            'User', back_populates='sessions')

class UserChat(Base):
    __tablename__ = 'user_chats'
    id = Column(Integer, primary_key=True)
    members = relationship(
            'User', secondary='user_chat_membership', back_populates='chats')
    messages = relationship(
            'ChatMessage', back_populates='chat', cascade='all, delete-orphan')

user_chat_membership = Table(
        'user_chat_membership',
        Base.metadata,
        Column('user_id', ForeignKey('users.id'), nullable=False, primary_key=True),
        Column('chat_id', ForeignKey('user_chats.id'), nullable=False, primary_key=True)
        )

class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    id = Column(Integer, nullable=False, primary_key=True)
    chat_id = Column(Integer, ForeignKey('user_chats.id'), nullable=False, primary_key=True)
    sender_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    message_type = Column(Integer, nullable=False)
    message_data = Column(LargeBinary, nullable=False)
    send_time = Column(TIMESTAMP, nullable=False)
    chat = relationship (
            'UserChat', back_populates='messages')

class InvalidCredentialsError(Exception):
    pass

