#!/bin/env python3
from models import *
from auth import *
from database import *

init_db()

def get_user(name):
    return session.query(User).where(User.username == name).one()

def get_or_create_user(name, email, passwd):
    try:
        return get_user(name)
    except NoResultFound:
        create_user(name, email, passwd)
        return get_user(name)


with Session() as session:
    torres = get_or_create_user('torres', 'torres@ekiwa.org', 'hola')
    ferran = get_or_create_user('ferran', 'baguette@molino.com', 'bolillo')
    cuadri = get_or_create_user('cuadri', 'añoña@nuevaalianza.com', 'azul')

    chat = UserChat(chat_type=ChatType.personal)
    chat.members.extend((torres, ferran))
    session.add(chat)
    session.commit()

