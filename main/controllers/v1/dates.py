from flask import request
from flask import g

from . import api
from main import db
from main.models.proposals import Proposal
from main.models.requests import Request
from main.models.dates import Date

from main.decorators import json
from main.decorators import paginate

from main.engines.restaurants import find_restaurant

@api.route('/dates/', methods=['GET'])
@json
@paginate('dates')
def get_dates():
	return Date.query


@api.route('/dates/<int:id>', methods=['GET'])
@json
def get_date(id):
	return Date.query.get_or_404(id).export_data()


@api.route('/proposals/<int:id>/dates/', methods=['POST'])
@json
def add_date(id):
	proposal = Proposal.query.get_or_404(id)
	if proposal.request.user != g.user:
		response = {
			'status': 401,
			'error': 'unauthorized',
			'message': 'you are not allowed to accept this proposal'
		}

		return response, 401
	
	restaurant_name = ''
	restaurant_address = ''
	restaurant = find_restaurant(proposal.request.meal_type, proposal.request.location_string)

	if restaurant:
		restaurant_name = restaurant['restaurant_name']
		restaurant_address = restaurant['restaurant_address']

	new_date = Date(
		proposal=proposal,
		restaurant_name=restaurant_name, 
		restaurant_address=restaurant_address
	)
	new_date.import_data(request.json)
	db.session.add(new_date)
	db.session.commit()

	return {}, 201, {'Location': new_date.get_url()}


@api.route('/dates/<int:id>', methods=['PUT'])
@json
def update_date(id):
	current_date = Date.query.get_or_404(id)
	if current_date.proposal.request.user != g.user:
		response = {
			'status': 401,
			'error': 'unauthorized',
			'message': 'you are not allowed to update this request'
		}

		return response, 401
		
	current_date.update_data(request.json)
	db.session.add(current_date)
	db.session.commit()

	return {}


@api.route('/dates/<int:id>', methods=['DELETE'])
@json
def delete_date(id):
	current_date = Date.query.get_or_404(id)
	if current_date.proposal.request.user != g.user:
		response = {
			'status': 401,
			'error': 'unauthorized',
			'message': 'you are not allowed to delete this request'
		}

		return response, 401
	db.session.delete(current_date)
	db.session.commit()

	return {}