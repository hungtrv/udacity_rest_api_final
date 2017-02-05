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

from flask import g
from main import app
from main import db
from main.config import config
from main.models.users import User
from main.models.requests import Request
from main.errors import ValidationError

from test_client import TestClient

API_VERSION = '/v1'

app.config.from_object(config)


class TestUsersAPI(unittest.TestCase):
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


	def test_misc(self):
		root_endpoint = API_VERSION + '/'
		rv, json = self.client.get(root_endpoint)
		self.assertTrue(rv.status_code == 200)


	def test_requests(self):
		requests_endpoint = API_VERSION + '/requests/'
		rv, json = self.client.get(requests_endpoint)
		self.assertTrue(rv.status_code == 200)
		self.assertTrue(len(json['requests']) == 0)

		# TODO: Fix this, the test doesn't catch the NotFound exception
		# with self.assertRaises(NotFound):
		# 	rv, json = self.client.get(requests_endpoint + '1')
		# 	self.assertTrue(rv.status == 200)

		# Add new request
		request_data = {
			'meal_type': 'Vietnamese',
			'meal_time': 'Dinner',
			'location_string': 'San Francisco'
		}
		rv, json = self.client.post(requests_endpoint, data=request_data)
		self.assertTrue(rv.status_code == 201)
		request_location = rv.headers['Location']
		rv, json = self.client.get(request_location)
		self.assertTrue(rv.status_code == 200)
		self.assertTrue(json['meal_time'] == request_data['meal_time'])
		self.assertTrue(json['meal_type'] == request_data['meal_type'])
		self.assertTrue(json['location_string'] == request_data['location_string'])
		self.assertTrue(json['user_url'].split('/')[-1] == str(g.user.id))

		rv, json = self.client.get(requests_endpoint)
		self.assertTrue(rv.status_code == 200)
		self.assertIn(request_location, json['requests'])

		# Edit a request
		new_request_data = {
			'meal_type': 'Japanese',
			'meal_time': 'Lunch',
			'location_string': 'Foster City'
		}
		rv, json = self.client.put(request_location, data=new_request_data)
		self.assertTrue(rv.status_code == 200)
		rv, json = self.client.get(request_location)
		self.assertTrue(rv.status_code == 200)
		self.assertTrue(json['meal_time'] == new_request_data['meal_time'])
		self.assertTrue(json['meal_type'] == new_request_data['meal_type'])
		self.assertTrue(json['location_string'] == new_request_data['location_string'])
		self.assertTrue(json['user_url'].split('/')[-1] == str(g.user.id))

		# Delete a request
		rv, json = self.client.delete(request_location)
		self.assertTrue(rv.status_code == 200)
		# TODO: Fix this, the test doesn't catch the NotFound exception
		# with self.assertRaises(NotFound):
		# 	rv, json = self.client.get(request_location)
		# 	self.assertTrue(rv.status_code == 200)




if __name__ == "__main__":
	suite = unittest.TestLoader().loadTestsFromTestCase(TestUsersAPI)
	unittest.TextTestRunner(verbosity=2).run(suite)
	COV.stop()
	COV.report()