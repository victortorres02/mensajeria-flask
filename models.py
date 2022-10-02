from sqlalchemy import Table, Column, ForeignKey, Integer, String, TIMESTAMP, LargeBinary
from sqlalchemy.orm import relationship
from enum import IntEnum
from datetime import datetime
from database import Base


class ChatType(IntEnum):
    personal = 1
    group = 2

class MessageType(IntEnum):
    text = 1


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
    chat_type = Column(Integer, nullable=False)
    name = Column(String(64), nullable=True)
    members = relationship(
            'User', secondary='user_chat_membership', back_populates='chats')
    messages = relationship(
            'ChatMessage', back_populates='chat', cascade='all, delete-orphan')

    db_filter_rules = {
            'since': ((datetime, int), lambda time: ChatMessage.send_time >= time),
            'message_type': (int, lambda type: ChatMessage.message_type == type),
            'sender_id': (int, lambda sender_id: ChatMessage.sender_id == sender_id),
            }
    @staticmethod
    def _db_filters(filter_by):
        db_filters = []
        for key in filter_by:
            rule = UserChat.db_filters.get(key, None)
            if rule:
                arg_type, func = rule
                val = filter_by[key]
                if not isinstance(val, arg_type):
                    raise ValueError('Invalid filter argument')
                db_filters.append(func(val))
        return db_filters

user_chat_membership = Table(
        'user_chat_membership',
        Base.metadata,
        Column('user_id', ForeignKey('users.id'), nullable=False, primary_key=True),
        Column('chat_id', ForeignKey('user_chats.id'), nullable=False, primary_key=True)
        )

class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    id = Column(Integer, nullable=False, primary_key=True)
    chat_id = Column(Integer, ForeignKey('user_chats.id'), nullable=False)
    sender_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    message_type = Column(Integer, nullable=False)
    message_size = Column(Integer, nullable=False)
    message_data = Column(LargeBinary, nullable=False)
    send_time = Column(TIMESTAMP, nullable=False)
    chat = relationship (
            'UserChat', back_populates='messages')

    @staticmethod
    def db_encode(message_data, message_type):
        message_type = MessageType(message_type)
        if message_type == MessageType.text:
            try:
                return message_data.encode('utf-8')
            except UnicodeEncodeError:
                raise ValueError

    @staticmethod
    def db_decode_message_data(message_data, message_type):
        if message_type == MessageType.text:
            try:
                return message_data.decode('utf-8')
            except UnicodeDecodeError:
                raise ValueError

    def db_decode_message(self):
        return self.db_decode_message_data(self.message_data, self.message_type)

class InvalidCredentialsError(Exception):
    pass

