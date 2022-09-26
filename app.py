from flask import Flask, request, abort, redirect, url_for
from auth import needs_session, create_session, InvalidCredentialsError

app = Flask(__name__)

@app.route('/')
def root():
    return redirect(url_for('login'))

@app.route('/favicon.ico')
def favicon():
    return redirect('/static/favicon.ico')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return redirect('/static/login.html')
    username = request.form['username']
    password = request.form['password']
    try:
        token = create_session(username, password)
        response = redirect('/static/webclient.html')
        response.set_cookie('user', secure=True, httponly=True, value=username)
        response.set_cookie('sid', secure=True, httponly=True, value=token)
        return response, 302
    except InvalidCredentialsError:
        abort(401)


@app.route('/api/web/post_msg', methods=['POST'])
@needs_session
def post_msg():
    chat_id = request.json['chat_id']
    payload = request.json['payload']
    app.logger.debug(f'chat_id <{chat_id}> payload <{payload}>')
    try:
        write_msg(chat_id, payload)
    except ValueError:
        abort(400)
    return 'Ok'

def write_msg(chat_id, payload):
    if isinstance(chat_id, int):
        chat_id = str(chat_id)
    if not isinstance(chat_id, str):
        raise ValueError
    if not chat_id.isnumeric():
        raise ValueError
    if not isinstance(payload, str):
        raise ValueError
    with open(chat_id, 'a') as file:
        file.write(payload + '\n')

def read_msg(chat_id, position):
    with open(chat_id, 'r') as file:
        file.seek(position)
        msg = file.readline()
        pos = file.tell()
        return msg, pos

@app.route('/api/web/get_msgs')
@needs_session
def get_msgs():
    chat_id = request.values['chat_id']
    position = request.values.get('position', 0, type=int)
    max_msgs = request.values.get('max_messages', 10, type=int)
    max_msgs = min(max(max_msgs, 1), 100)
    pos = position
    msgs = []
    try:
        for i in range(max_msgs):
            msg, pos = read_msg(chat_id, pos)
            if not msg:
                break
            msgs.append({
                'payload':msg.replace('\n', ''),
                'position':pos
                })
    except ValueError:
        abort(400)
    except FileNotFoundError:
        return {'messages':[]}
    return {
            'messages':msgs,
            }


