from flask import jsonify
from flask import g

from main import app
from main import auth
from main import auth_token

from main.models.users import User

from main.decorators import json

@auth.verify_password
def verify_password(username, password):
	g.user = User.query.filter_by(username=username).first()
	if g.user is None:
		return False

	return g.user.verify_password(password)

@auth.error_handler
@json
def unauthorize():
	response = {
		'status': 401,
		'error': 'unauthorized',
		'message': 'please authenticate'
	}

	return response, 401


@app.route('/email/login')
@auth.login_required
@json
def email_login():
	return {'token': g.user.generate_auth_token()}


@app.route('/email/logout')
@json
def email_logout():
	# Need to work on how to invalidate a token
	return {}