from flask import request, abort
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import and_
from sqlalchemy.exc import NoResultFound
from secrets import token_urlsafe
from datetime import datetime
from database import Session
from models import User, SessionId, InvalidCredentialsError


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
        session.add(SessionId(
            token=token, user_id=user.id,
            creation_time=timestamp, last_use_time=timestamp))
        session.commit()
        return token

def create_user(username, email, password):
    with Session() as session:
        session.add(User(
            username=username, email=email,
            hashed_password=generate_password_hash(password)))
        session.commit()

def session_is_valid(username, token):
    with Session() as session:
        try:
            session_id = session.query(SessionId).join(User).where(
                    and_(
                        User.username == username,
                        SessionId.token == token)
                    ).one()
            return True
        except NoResultFound:
            return False

def needs_session(func, handler=lambda args:abort(401)):
    def auth_wrapper(**kwargs):
        username = request.cookies.get('user')
        token = request.cookies.get('sid')
        if username and token and session_is_valid(username, token):
            return func(**kwargs)
        else:
            return handler(kwargs)
    auth_wrapper.__name__ = func.__name__
    return auth_wrapper

