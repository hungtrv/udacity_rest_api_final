from base64 import b64encode
import os
import sys
current_dir = os.path.abspath(os.path.dirname(__file__))
app_dir = os.path.abspath(os.path.join(current_dir, '../'))
sys.path.insert(0, app_dir)
os.environ['ENVIRONMENT'] = 'test'

import pytest
from main import app
from main import db
from main.config import config
from main.models.users import User
app.config.from_object(config)

API_VERSION = '/v1'

@pytest.fixture
def client():
	test_client = app.test_client()
	db.drop_all()
	db.create_all()
	user = User(username='hungtrv')
	user.set_password_hash('123456')
	db.session.add(user)
	db.session.commit()

	yield test_client
	
	"""
		tearDown code
	"""
	db.session.remove()
	db.drop_all()


def test_failed_login(client):
	rv = client.get('/email/login')
	assert rv.status_code == 401


@pytest.mark.parametrize('username, password', [('hungtrv', '123456')])
def test_login(client, username, password):
	client_auth = 'Basic ' + b64encode((username + ':' + password).encode('utf-8').decode('utf-8'))
	rv = client.get('/email/login', headers={'Authorization': client_auth})
	assert rv.status_code == 200
	assert 'token' in rv.data