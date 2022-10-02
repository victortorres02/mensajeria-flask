from flask import request, abort
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import and_
from sqlalchemy.exc import NoResultFound
from secrets import token_urlsafe
from datetime import datetime, timedelta
from database import Session
from models import User, SessionId, InvalidCredentialsError
from db_utils import using_db_session, using_db_user
from utils import ResourceDecorator


def create_session(username, password):
    with Session() as session:
        try:
            user = session.query(User).where(User.username == username).one()
        except NoResultFound:
            session.close()
            raise InvalidCredentialsError('Invalid username')
        if not check_password_hash(user.hashed_password, password):
            session.close()
            raise InvalidCredentialsError('Invalid password')
        token = token_urlsafe(48)
        timestamp = datetime.now()
        expire_time = timestamp + timedelta(hours=1)
        session.add(SessionId(
            token=token, user_id=user.id,
            creation_time=timestamp, last_use_time=timestamp,
            expire_time=expire_time))
        session.commit()
        return token

def create_user(username, email, password):
    with Session() as session:
        session.add(User(
            username=username, email=email,
            hashed_password=generate_password_hash(password)))
        session.commit()

def session_is_valid(user, token, session, update_last_use_time=True):
        try:
            session_id = session.query(SessionId).join(User).where(
                    and_(
                        User.id == user.id,
                        SessionId.token == token)
                    ).one()
            timestamp = datetime.now()
            if timestamp >= session_id.expire_time:
                session.query(SessionId).where(
                        SessionId.expire_time <= timestamp).delete()
                return False
            if update_last_use_time:
                session_id.last_use_time = timestamp
            return True
        except NoResultFound:
            return False

def require_session(func, handler=lambda args:abort(401)):
    @using_db_session
    @using_db_user
    def auth_wrapper(user, session, **kwargs):
        token = request.cookies.get('sid')
        if token and session_is_valid(user, token, session):
            return func(user=user, session=session, **kwargs)
        else:
            return handler(kwargs)
    auth_wrapper.__name__ = func.__name__
    return auth_wrapper

