from werkzeug.security import check_password_hash, generate_password_hash
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

