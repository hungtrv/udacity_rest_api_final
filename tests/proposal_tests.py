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

from test_client import TestClient

API_VERSION = '/v1'

app.config.from_object(config)


class TestProposalsAPI(unittest.TestCase):
	default_username = 'hungtrv'
	default_password = '123456'


	def setUp(self):
		self.app = app
		self.ctx = self.app.app_context()
		self.ctx.push()
		db.drop_all()
		db.create_all()

		# Creating the 1st user. This user will issue a request
		user = User(username=self.default_username)
		user.set_password_hash(self.default_password)
		db.session.add(user)
		db.session.commit()
		self.client = TestClient(self.app, user.generate_auth_token(), '')

		# Create a request for 1st user
		request_data = {
			'meal_type': 'Vietnamese',
			'meal_time': 'Dinner',
			'location_string': 'San Francisco'
		}
		rv, json = self.client.post(API_VERSION + '/requests/', data=request_data)
		self.request_location = rv.headers['Location']

		# Create the 2nd user. This user will make proposal for the request by 1st user
		user_2 = User(username='proposer')
		user_2.set_password_hash('123456')
		db.session.add(user_2)
		db.session.commit()
		self.client = TestClient(self.app, user_2.generate_auth_token(), '')
		

	def tearDown(self):
		db.session.remove()
		db.drop_all()
		self.ctx.pop()


	def test_misc(self):
		root_endpoint = API_VERSION + '/'
		rv, json = self.client.get(root_endpoint)
		self.assertTrue(rv.status_code == 200)


	def test_proposals(self):
		proposals_endpoint = API_VERSION + '/proposals/'
		rv, json = self.client.get(proposals_endpoint)
		self.assertTrue(rv.status_code == 200)
		self.assertTrue(len(json['proposals']) == 0)

		# Add new proposal
		rv, json = self.client.get(self.request_location)
		self.assertTrue(rv.status_code == 200)

		proposals_url = json['proposals_url']
		rv, json = self.client.post(proposals_url, data={'a':'b'})
		self.assertTrue(rv.status_code == 201)

		proposal_location = rv.headers['Location']
		rv, json = self.client.get(proposal_location)
		self.assertTrue(rv.status_code == 200)
		self.assertTrue(json['request_url'] == self.request_location)
		self.assertTrue(json['self_url'] == proposal_location)
		self.assertTrue(json['user_url'].split('/')[-1] == str(g.user.id))

		rv, json = self.client.get(proposals_url)
		self.assertTrue(rv.status_code == 200)
		self.assertIn(proposal_location, json['proposals'])

		# Update proposal
		rv, json = self.client.put(proposal_location, data={'accepted': True})
		self.assertTrue(rv.status_code == 200)

		rv, json = self.client.get(proposal_location)
		self.assertTrue(rv.status_code == 200)
		self.assertTrue(json['accepted'] == True)

		# Delete proposal
		rv, json = self.client.delete(proposal_location)
		self.assertTrue(rv.status_code == 200)

		with self.assertRaises(NotFound):
			rv, json = self.client.get(proposal_location)


if __name__ == "__main__":
	suite = unittest.TestLoader().loadTestsFromTestCase(TestProposalsAPI)
	unittest.TextTestRunner(verbosity=2).run(suite)
	COV.stop()
	COV.report()