from flask import Blueprint, request, abort, redirect, url_for
from werkzeug.datastructures import MultiDict, ImmutableMultiDict
import werkzeug
from sqlalchemy import select, and_
from sqlalchemy.exc import NoResultFound
from datetime import datetime
import traceback
from models import User, UserChat, ChatType, ChatMessage, MessageType
from auth import require_session
from db_utils import using_db_session, using_db_user
from utils import json_abort

bp = Blueprint('web_api', __name__, url_prefix='/api/web')

@bp.errorhandler(werkzeug.exceptions.Unauthorized)
def api_unauthorized(error):
    return {
            'status': 'error',
            'reason': 'unauthorized'
            }

@bp.route('/list_contacts', methods=['GET', 'POST'])
@require_session
def list_contacts(user, session):
    contacts = {
            'status': 'ok',
            'contacts': [{
                'id': contact.id,
                'use/rname': contact.username,
                # TODO: implementar los contactos!
                } for contact in session.query(Users).all()]
            }
    session.commit()
    return contacts

@bp.route('/list_chats', methods=['GET', 'POST'])
@require_session
def list_chats(user, session):
    chats = {
            'status': 'ok',
            'chats': [{
                'id': chat.id,
                'name': chat.name,
                'type': chat.chat_type,
                'members': [{
                    'id': member.id,
                    'username': member.username,
                    } for member in chat.members],
                } for chat in user.chats]
            }
    session.commit()
    return chats

@bp.route('/create_chat', methods=['GET', 'POST'])
@require_session
def create_chat(user, session):
    user_id = request.json['user_id']
    chat_type = request.json['chat_type']
    try:
        chat_type = ChatType(chat_type)
    except ValueError:
        json_abort('Invalid chat_type')

    if user_id == user.id:
        json_abort('Invalid user id')
    try:
        other_user = session.query(User).where(User.id == user_id).one()
    except NoResultFound:
        json_abort('Invalid user')

    if chat_type == ChatType.personal:
        if session.query(UserChat).where(and_(
            UserChat.members.contains(user),
            UserChat.members.contains(other_user),
            UserChat.chat_type == ChatType.personal,
            )).one_or_none() is not None:
                json_abort('Personal chat already created')

    chat = UserChat(chat_type=chat_type)
    chat.members.extend((user, other_user))
    session.add(chat)
    session.commit()
    return {
            'status': 'ok',
            'id': chat.id,
            }

@bp.route('/list_messages', methods=['POST'])
@require_session
def list_messages(user, session):
    chat_id = request.json['chat_id']
    max_messages = request.json.get('max_messages', 1000)
    filter_by = request.json.get('filter_by', {})
    if not isinstance(max_messages, int) or\
            not isinstance(filter_by, (dict, MultiDict, ImmutableMultiDict)):
        json_abort('Invalid filter_by argument')

    try:
        chat = session.query(UserChat).where(
                and_(UserChat.id == chat_id, UserChat.members.contains(user))).one()
    except NoResultFound:
        json_abort('Invalid chat_id')

    try:
        chat_filters = UserChat._db_filters(filter_by)
    except ValueError:
        json_abort('Invalid chat filter argument')

    messages_sel = select(
            ChatMessage.id, ChatMessage.sender_id,
            ChatMessage.message_type, ChatMessage.message_size)\
            .where(and_(ChatMessage.chat_id == chat.id, *chat_filters))\
            .order_by(ChatMessage.send_time).limit(max_messages)
    messages = {
            'status': 'ok',
            'messages': [{
                'id': id,
                'sender_id': sender_id,
                'message_type': message_type,
                'message_size': message_size,
                } for id, sender_id, message_type, message_size in session.execute(messages_sel)]
            }
    session.commit()
    return messages

@bp.route('/retrieve_messages', methods=['POST'])
@require_session
def retrieve_messages(user, session):
    chat_id = request.json['chat_id']
    message_ids = request.json['message_ids']
    if not isinstance(message_ids, list) or not all(isinstance(id, int) for id in message_ids):
        json_abort('Invalid argument type')

    try:
        chat = session.query(UserChat).where(
                and_(UserChat.id == chat_id, UserChat.members.contains(user))).one()
    except NoResultFound:
        json_abort('Invalid chat_id')

    max_data_size = 8388608 # 8MB
    messages = []
    data_size = 0
    for id in message_ids:
        if data_size > max_data_size:
            break

        try:
            message = session.query(ChatMessage).where(and_(
                ChatMessage.chat_id == chat.id,
                ChatMessage.id == id,
                )).one()
        except NoResultFound:
            messages.append({
                'id': id,
                'status': 'error',
                'reason': 'chat_id not found',
                })
            continue

        data_size += message.message_size

        try:
            data = message.db_decode_message()
        except ValueError:
            print('<---------- Integrity error ---------->',
                  '\n', f'user_id: {user.id}, message_id: {ChatMessage.id}',
                  '\n', traceback.format_exc(), '\n'
                  'Ignoring exception and continuing ...')
            continue

        messages.append({
            'id': id,
            'sender_id': message.sender_id,
            'message_type': message.message_type,
            'message_size': message.message_size,
            'message_data': data,
            })

    messages = {
            'status': 'ok',
            'messages': messages
            }
    session.commit()
    return messages

@bp.route('/send_message', methods=['POST'])
@require_session
def send_message(user, session):
    chat_id = request.json['chat_id']
    message_data = request.json['message_data']
    message_type = request.json.get('message_type', MessageType.text)

    if not isinstance(message_data, (str, bytes)):
        json_abort('Invalid argument type')

    try:
        message_type = MessageType(message_type)
    except ValueError:
        json_abort('Invalid message_type')

    try:
        chat = session.query(UserChat).where(
                and_(UserChat.id == chat_id, UserChat.members.contains(user))).one()
    except NoResultFound:
        json_abort('Invalid chat_id')

    try:
        data = ChatMessage.db_encode(message_data, message_type)
    except ValueError:
        json_abort('Invalid message data')

    message = ChatMessage(
        sender_id=user.id, chat_id=chat.id,
        send_time=datetime.now(),
        message_type=message_type, message_size=len(data),
        message_data=data
        )
    session.add(message)
    session.commit()
    return {
            'status': 'ok'
            }


