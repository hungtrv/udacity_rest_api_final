import os

from flask import g
from flask import jsonify
from flask import request
from flask import url_for
from flask import redirect

from main import app
from main import db
from main.controllers.v1 import api
from main import auth
from main import auth_token

from main.models.users import User

from main.decorators import json
from main.decorators import rate_limit
from main.decorators import no_cache
from main.decorators import etag

from oauth2client.client import OAuth2WebServerFlow
from apiclient import discovery
import httplib2

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


@api.before_request
@auth_token.login_required
@rate_limit(limit=5, period=15) # Only allow 5 requests within 15 seconds
def before_request():
	pass


@api.after_request
@etag
def after_request(rv):
	return rv


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


@app.route('/google/login')
def google_login():
	flow = OAuth2WebServerFlow(
			client_id=app.config['GOOGLE_OAUTH2_CLIENT_ID'],
			client_secret=app.config['GOOGLE_OAUTH2_CLIENT_SECRET'],
			scope='email',
			redirect_uri = url_for('google_login', _external=True)
		)
	
	if 'code' not in request.args:
		auth_uri = flow.step1_get_authorize_url()
		return redirect(auth_uri)

	elif 'code' in request.args:
		auth_code = request.args.get('code')
		credentials = flow.step2_exchange(auth_code)
		http_auth = credentials.authorize(httplib2.Http())
		plus_service = discovery.build('plus', 'v1', http_auth)
		user = plus_service.people().get(userId='me').execute()
		user_data = {
			'username': user['emails'][0]['value'].split('@')[0],
			'email': user['emails'][0]['value'],
			'photo_url': user['image']['url'],
			'password': os.urandom(24)
		}

		tmp_user = User.query.filter_by(username=user_data['username']).first()
		
		if tmp_user is None:
			new_user = User()
			new_user.import_data(user_data)
			db.session.add(new_user)
			db.session.commit()
			tmp_user = new_user

		return jsonify({'token': tmp_user.generate_auth_token()})

	else:
		response = jsonify({
        	'status': 401,
        	'error': 'access denied',
        	'message': 'user does not authorized access'
    	})
    	response.status_code = 401

    	return response
