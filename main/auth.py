from flask import g

from main import app
from main.controllers.v1 import api
from main import auth
from main import auth_token

from main.models.users import User

from main.decorators import json
from main.decorators import rate_limit
from main.decorators import no_cache
from main.decorators import etag

"""
	auth: HTTP Authentication used with main app for login, logout, authentication token
"""
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

"""
	auth_token: HTTP Authentication used with API endpoints
"""
@auth_token.verify_password
def verify_auth_token(token, unused_password):
	g.user = User.verify_auth_token(token)

	return g.user is not None


@auth_token.error_handler
@json
def unauthorized_token():
	response = {
		'status': 401,
		'error': 'unauthorized',
		'message': 'please send your authentication token'
	}

	return response, 401


@app.route('/email/login')
@auth.login_required
@rate_limit(limit=1, period=600) # Only allow 1 call within 600 second
@no_cache
@json
def email_login():
	return {'token': g.user.generate_auth_token()}


@app.route('/email/logout')
@json
def email_logout():
	# Need to work on how to invalidate a token
	return {}

@api.before_request
@auth_token.login_required
@rate_limit(limit=5, period=15) # Only allow 5 requests within 15 seconds
def before_request():
	pass


@api.after_request
@etag
def after_request(rv):
	return rv