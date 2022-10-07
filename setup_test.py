#!/bin/env python3
from models import *
from auth import *
from database import *

init_db()

create_user('torres', 'torres@ekiwa.org', 'hola')
create_user('ferran', 'baguette@molino.com', 'bolillo')

with Session() as session:
    torres = session.query(User).where(User.username == 'torres').one()
    ferran = session.query(User).where(User.username == 'ferran').one()

    chat = UserChat(chat_type=ChatType.personal)
    chat.members.extend((torres, ferran))
    session.add(chat)
    session.commit()

