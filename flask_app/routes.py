# Author: Prof. MM Ghassemi <ghassem3@msu.edu>
from flask import current_app as app
from flask import render_template, redirect, request, session, url_for, copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
from .utils.database.database  import database
from werkzeug.datastructures   import ImmutableMultiDict
from pprint import pprint
import json
import random
import functools
from . import socketio
db = database()


#######################################################################################
# AUTHENTICATION RELATED
#######################################################################################
def login_required(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if "email" not in session:
            return redirect(url_for("login", next=request.url))
        return func(*args, **kwargs)
    return secure_function

def getUser():
    user = session['email'] if 'email' in session else 'Unknown'
    if user != 'Unknown':
        user = db.reversibleEncrypt('decrypt', user)
    return user

@app.route('/login')
def login():
	return render_template('login.html', id=db.getUserCurrentBoard(getUser()))

@app.route('/logout')
def logout():
	session.pop('email', default=None)
	return redirect('/')

@app.route('/processlogin', methods = ["POST","GET"])
def processlogin():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
   
    auth = db.authenticate(form_fields['email'], form_fields['password'])

    if auth['success'] == 1:
        session['email'] = db.reversibleEncrypt('encrypt', form_fields['email']) 
        return json.dumps({'success':1})

    return json.dumps({'success':0})

def getRole():
     role = db.getRole(getUser())
     if role != 'N/A':
          return role
     return 'N/A'

@app.route('/signup')
def signup():
     return render_template('signup.html', id=db.getUserCurrentBoard(getUser()))

@app.route('/processsignup', methods = ["POST","GET"])
def processsignup():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    email = form_fields['email']

    account_exists = db.accountExists(email)
    # Email is not used and the passwords match
    if not account_exists and form_fields['password'] == form_fields['confirm']:
        # Create user
        print("Creating User:" + email + ", " + form_fields['password'])
        db.createUser(email, form_fields['password'])
        return json.dumps({'success':1})
    
    # Unknown Error!
    return json.dumps({'success':0})

#######################################################################################
# CHAT RELATED
#######################################################################################

@socketio.on('joined', namespace='/workspace')
def joined(message):
    join_room('main')
    
    emit('status', {'msg': getUser() + ' has entered the room.', 'style': 'width: 100%;color:gray;text-align: left'}, room='main')
    
@socketio.on('message', namespace='/workspace')
def message(msg):

    emit('status', {'msg': getUser() + ": " + str(msg['message']), 'style': 'width: 100%;color:gray;text-align: left'}, room='main')
    

@socketio.on('left', namespace='/workspace')
def left(message):

    emit('status', {'msg': getUser() + ' has left the room.', 'style': 'width: 100%;color:gray; text-align: left'}, room='main')
    
    leave_room('main')

#######################################################################################
# BOARD RELATED
#######################################################################################
@app.route('/createboard', methods = ["POST","GET"])
def createboard():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    
    
    if (form_fields['boardName']):
        db.insertRows('boards', ['name','background_img'], [form_fields['boardName'], 'background1.png'])

        query = f"""SELECT * FROM boards"""
        result = db.query(query)

        id = None

        for board in result:
            if (form_fields['boardName'] == board['name']):
                id = board['board_id']


        if (not id):
            return json.dumps({'success':0})
        
        query = f"""SELECT * FROM users"""
        result = db.query(query)

        query = "UPDATE users SET board_id = {}".format(id)
        db.query(query)

        fields = ['board_id', 'name']
        params = [id, "To Do"]

        db.insertRows('lists', fields, params)

        params = [id, "Doing"]

        db.insertRows('lists', fields, params)

        params = [id, "Completed"]

        db.insertRows('lists', fields, params)

        # add creator to auth
        fields = ['board_id', 'email']
        params = [id, getUser()]
        db.insertRows('auth', fields, params)

        return json.dumps({'success':1})

    return json.dumps({'success':0})

@app.route('/loadboardoptions')
def loadboardoptions():
    user = getUser()

    query = "SELECT board_id, email FROM auth WHERE email = {}".format(user)
    result = db.query(query)

    return json.dumps({'success':1, 'result': result})

@app.route('/addusertoboard', methods = ["POST","GET"])
def addusertoboard():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))

    print("trying email: ", form_fields['userName'])
    query = "SELECT email FROM users"
    result = db.query(query)

    for account in result:
        print("Trying: " + form_fields['userName'] + " vs: " + account['email'])
        if (form_fields['userName'] == account['email']):
            print("Email found!")
            # add to db
            fields = ['board_id', 'email']
            params = [db.getUserCurrentBoard(getUser()), str(form_fields['userName'])]
            db.insertRows('auth', fields, params)
            return json.dumps({'success':1})

    return json.dumps({'success':0})


@app.route('/loadlist', methods = ["POST","GET"])
def loadlist():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))

    id = db.getUserCurrentBoard(getUser())

    query = "SELECT * FROM lists WHERE board_id = {}".format(id)

    result = db.query(query)
    
    return json.dumps({'success':1, 'lists': result})
    
@app.route('/workspace')
@login_required
def workspace():
     
    name = db.getCurrentBoardName(getUser())
    Id = db.getUserCurrentBoard(getUser())
    
    return render_template('workspace.html', boardName=name, user=getUser(), id=Id)

@app.route('/createlist', methods = ["POST","GET"])
def createlist():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    fields = ['board_id', 'name']
    params = [form_fields['board_id'], form_fields['name']]

    db.insertRows('lists', fields, params)

    return json.dumps({'success':1})

@app.route('/createtask', methods = ["POST","GET"])
def createtask():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    fields = ['list_id', 'name', 'position']
    params = [form_fields['list_id'], form_fields['name'], 99]

    db.insertRows('cards', fields, params)

    return json.dumps({'success':1})

@app.route('/loadtask', methods = ["POST","GET"])
def loadtask():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))

    list_id = form_fields['list_id']

    query = "SELECT * FROM cards WHERE list_id = {}".format(list_id)

    result = db.query(query)

    return json.dumps({'success':1, 'tasks': result})


#######################################################################################
# OTHER
#######################################################################################
@app.route('/')
@login_required
def root():
	return redirect('/home')

@app.route('/home')
def home():
	return render_template('home.html', active_page='home')

@app.route('/projects')
def projects():
	return render_template('projects.html', active_page='projects')

@app.route('/contact')
def contact():
	return render_template('contact.html', active_page='contact')

@app.route("/static/<path:path>")
def static_dir(path):
    return send_from_directory("static", path)

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r


