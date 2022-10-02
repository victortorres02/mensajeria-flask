from flask import request, abort
from models import User
from database import Session
from sqlalchemy.exc import NoResultFound
from utils import ResourceDecorator

using_db_session = ResourceDecorator('session')
@using_db_session.set_wrapper
def session_wrapper(wrapped_func, kwargs):
    if 'session' in kwargs:
        return wrapped_func(**kwargs)
    with Session() as session:
        print('<<< Created session >>>')
        return wrapped_func(session=session, **kwargs)

using_db_user = ResourceDecorator('user')
@using_db_user.set_generator(pass_arguments=True)
@using_db_session
def user_lookup(session, **kwargs):
    username = request.cookies.get('user')
    if not username:
        abort(400, 'Webapi needs a set user')
    try:
        user = session.query(User).where(User.username == username).one()
    except NoResultFound:
        abort(400, 'Invalid User')
    return user


