import coverage
COV = coverage.coverage(branch=True, include='main*')
COV.start()

from werkzeug.exceptions import NotFound
import unittest
import os
import sys
current_dir = os.path.abspath(os.path.dirname(__file__))
app_dir = os.path.abspath(os.path.join(current_dir, '../'))
sys.path.insert(0, app_dir)

os.environ['ENVIRONMENT'] = 'test'

from main import app
from main import db
from main.config import config
from main.models.users import User
from main.errors import ValidationError

from test_client import TestClient

API_VERSION = '/v1'

app.config.from_object(config)


class TestAPI(unittest.TestCase):
	default_username = 'hungtrv'
	default_password = '123456'

	def setUp(self):
		self.app = app
		self.ctx = self.app.app_context()
		self.ctx.push()
		db.drop_all()
		db.create_all()
		user = User(username=self.default_username)
		user.set_password_hash(self.default_password)
		db.session.add(user)
		db.session.commit()
		self.client = TestClient(self.app, user.generate_auth_token(), '')


	def tearDown(self):
		db.session.remove()
		db.drop_all()
		self.ctx.pop()


	def test_users(self):
		# Get list of all users
		users_endpoint = API_VERSION + '/users/'
		rv, json = self.client.get(users_endpoint)
		self.assertTrue(rv.status_code == 200)
		self.assertTrue(len(json['users']) == 1)

		# Add a new user
		user_data = {
						'username': 'user_1', 
						'password': '123456', 
						'email': 'user_1@gotitapp.co', 
						'photo_url': 'http://www.gotitapp.co/user.jpg'
					}

		rv, json = self.client.post(users_endpoint, data=user_data)
		self.assertTrue(rv.status_code == 201)
		location = rv.headers['Location']
		rv, json = self.client.get(location)
		self.assertTrue(rv.status_code == 200)
		self.assertTrue(json['username'] == user_data['username'])
		self.assertTrue(json['email'] == user_data['email'])
		self.assertTrue(json['photo_url'] == user_data['photo_url'])

		# Add a duplicated user
		duplicated_user_data = {
						'username': 'user_1', 
						'password': '123', 
						'email': 'user_2@gotitapp.co', 
						'photo_url': 'http://www.gotitapp.co/user_2.jpg'
					}
		with self.assertRaises(ValidationError) as context:
			rv, json = self.client.post(users_endpoint, data=duplicated_user_data)
			self.assertTrue('Username already existed!' in context.exception)

		# Edit a user
		updated_user_data = {
						'username': 'user_2', 
						'email': 'user_2@gotitapp.co', 
						'photo_url': 'http://www.gotitapp.co/user2.jpg'
					}

		rv, json = self.client.put(location, data=updated_user_data)
		self.assertTrue(rv.status_code == 200)
		rv, json = self.client.get(location)
		self.assertTrue(rv.status_code == 200)
		self.assertTrue(json['username'] == updated_user_data['username'])
		self.assertTrue(json['email'] == updated_user_data['email'])
		self.assertTrue(json['photo_url'] == updated_user_data['photo_url'])

		# Delete a user
		rv, json = self.client.delete(location)
		self.assertTrue(rv.status_code == 200)

		with self.assertRaises(NotFound) as context:
			rv, json = self.client.get(location)
			self.assertTrue('Not Found' in context.exception)



if __name__ == "__main__":
	suite = unittest.TestLoader().loadTestsFromTestCase(TestAPI)
	unittest.TextTestRunner(verbosity=2).run(suite)
	COV.stop()
	COV.report()