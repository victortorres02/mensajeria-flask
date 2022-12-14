from flask import Flask, request, abort, redirect, url_for, send_file, send_from_directory
from auth import create_session, InvalidCredentialsError
import api.web

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

@app.route('/static/webclient.js')
def webclient_js():
    return send_file('static/webclient.js', mimetype='text/javascript')

@app.route('/static/webclient/<path:name>')
def webclient_dir(name):
    return send_from_directory('static/webclient', name, mimetype='text/javascript')

app.register_blueprint(api.web.bp)

