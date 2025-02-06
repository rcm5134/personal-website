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
# PROJECT RELATED
#######################################################################################

@app.route('/loadprojects', methods = ["POST", "GET"])
def loadprojects():
    data = request.get_json()  # Extract JSON data properly
    selected_skills = data.get("filters", []) 

    if not selected_skills:
        # If no skills are selected, return all projects
        query = "SELECT * FROM projects"
        result = db.query(query)
    else:
        # Construct query to find projects that have at least one of the selected skills
        placeholders = ', '.join(['%s'] * len(selected_skills))  # For IN clause
        query = f"""
        SELECT DISTINCT p.*
        FROM projects p
        JOIN skills s ON p.proj_id = s.proj_id
        WHERE s.name IN ({placeholders});
        """
        
        result = db.query(query, tuple(selected_skills)) 
    
    return json.dumps({'success':1, 'projects': result})

@app.route('/loadfilters', methods = ["POST", "GET"])
def loadfilters():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))

    query = "SELECT DISTINCT name FROM skills"

    result = db.query(query)
    
    return json.dumps({'success':1, 'filters': result})



#######################################################################################
# OTHER
#######################################################################################
@app.route('/')
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


