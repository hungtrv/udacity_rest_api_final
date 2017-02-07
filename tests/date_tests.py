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


class TestDatesAPI(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.drop_all()
        db.create_all()

        # Creating the 1st user. This user will issue a request
        requester = User(username='requester')
        requester.set_password_hash('password_1')
        db.session.add(requester)
        db.session.commit()
        self.requester = requester
        self.client_1 = TestClient(
            self.app, requester.generate_auth_token(), '')

        # Create a request for 1st user
        request_data = {
            'meal_type': 'Vietnamese',
            'meal_time': 'Dinner',
            'location_string': 'San Francisco'
        }
        rv, json = self.client_1.post(
            API_VERSION + '/requests/', data=request_data)
        self.request_location = rv.headers['Location']

        # Create the 2nd user. This user will make proposal for the request by
        # 1st user
        proposer = User(username='proposor')
        proposer.set_password_hash('password_1')
        db.session.add(proposer)
        db.session.commit()
        self.client_2 = TestClient(
            self.app, proposer.generate_auth_token(), '')

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_misc(self):
        root_endpoint = API_VERSION + '/'
        rv, json = self.client_1.get(root_endpoint)
        self.assertTrue(rv.status_code == 200)

    def test_dates(self):
        proposals_endpoint = API_VERSION + '/dates/'
        rv, json = self.client_1.get(proposals_endpoint)
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(len(json['dates']) == 0)

        # Proposer add a proposal for the request by Requester
        rv, json = self.client_2.get(self.request_location)
        self.assertTrue(rv.status_code == 200)

        proposals_url = json['proposals_url']
        rv, json = self.client_2.post(proposals_url, data={'foo': 'bar'})
        self.assertTrue(rv.status_code == 201)
        proposal_location = rv.headers['Location']
        rv, json = self.client_2.get(proposal_location)
        date_url = json['date_url']
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['request_url'] == self.request_location)
        self.assertTrue(json['self_url'] == proposal_location)
        self.assertTrue(json['user_url'].split('/')[-1] == str(g.user.id))

        # Requester accept a proposal
        rv, json = self.client_1.post(date_url, data={'foo': 'bar'})
        self.assertTrue(rv.status_code == 201)
        date_location = rv.headers['Location']
        rv, json = self.client_1.get(date_location)
        self.assertTrue(rv.status_code == 200)
        rv, json = self.client_2.get(date_location)
        self.assertTrue(rv.status_code == 200)

        # Requester update a date
        rv, json = self.client_1.put(
            date_location, data={'restaurant_name': 'Japanese'})
        self.assertTrue(rv.status_code == 200)
        rv, json = self.client_1.get(date_location)
        self.assertTrue(rv.status_code == 200)
        self.assertTrue(json['restaurant_name'] == 'Japanese')

        # Requester delete a date
        rv, json = self.client_1.delete(date_location)
        self.assertTrue(rv.status_code == 200)
        with self.assertRaises(NotFound):
            rv, json = self.client_1.get(date_location)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDatesAPI)
    unittest.TextTestRunner(verbosity=2).run(suite)
    COV.stop()
    COV.report()
