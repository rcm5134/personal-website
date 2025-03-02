# Author: Prof. MM Ghassemi <ghassem3@msu.edu>

#--------------------------------------------------
# Import Requirements
#--------------------------------------------------
import os
from flask import Flask
from flask_socketio import SocketIO
from flask_failsafe import failsafe

socketio = SocketIO()

#--------------------------------------------------
# Create a Failsafe Web Application
#--------------------------------------------------
@failsafe
def create_app(debug=False):
	app = Flask(__name__)

	# NEW IN HOMEWORK 3 ----------------------------
	# This will prevent issues with cached static files
	app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
	app.debug = debug
	# The secret key is used to cryptographically-sign the cookies used for storing the session data.
	app.secret_key = 'AKWNF1231082fksejfOSEHFOISEHF24142124124124124iesfhsoijsopdjf'
	# ----------------------------------------------

	from .utils.database.database import database
	db = database()
	db.createTables(purge=True)

	db.createProject("Pacman AI Maze Search", "pacman.png", "Found optimal cost paths for a Pacman Agent by implementing Dijkstra's algorithm, A*, DFS, BFS, and more!", "https://www.github.com", 1,['Python'])
	db.createProject("Connect Four Machine Learning", "connectfour.png", 'Used Machine Learning techniques such as CNN, MLP, SVM, Decision Tree, and Reinforcement Learning to create a Connect Four Bot.', "https://github.com/kjowak/cse-404-fs24-connect-four-bot", 1,['Python'])
	db.createProject("Traffic Jam Assist Prototype", "tja.png", 'Collaborated with four team members and customers to create a Software Requirement Specification document and rapid prototype for safety critical car systems.', "https://cse.msu.edu/~tamayoa3/prototype.html", 1, ["C#", "Unity", "UML"])
	db.createProject("Personal Website", "personal.png", 'Mobile friendly personal website for Riley Moorman using HTML, CSS, Python, SQL, and vanilla JavaScript', "https://github.com/rcm5134/personal-website", 0,["JavaScript", "SQL", "CSS", "HTML", "Python"])

	socketio.init_app(app)

	with app.app_context():
		from . import routes
		return app
