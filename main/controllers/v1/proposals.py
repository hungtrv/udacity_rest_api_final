from flask import request
from flask import g

from . import api
from main import db
from main.models.proposals import Proposal
from main.models.requests import Request

from main.decorators import json
from main.decorators import paginate


@api.route('/proposals/', methods=['GET'])
@json
@paginate('proposals')
def get_propsals():
	return Proposal.query


@api.route('/proposals/<int:id>', methods=['GET'])
@json
def get_proposal(id):
	return Proposal.query.get_or_404(id).export_data()


@api.route('/requests/<int:id>/proposals/', methods=['GET'])
@json
@paginate('proposals')
def get_request_proposals(id):
	current_request = Request.query.get_or_404(id)

	return current_request.proposals


@api.route('/requests/<int:id>/proposals/', methods=['POST'])
@json
def add_proposal(id):
	current_request = Request.query.get_or_404(id)
	new_proposal = Proposal(request=current_request, user=g.user)
	new_proposal.import_data(request.json)
	db.session.add(new_proposal)
	db.session.commit()

	return {}, 201, {'Location': new_proposal.get_url()}


@api.route('/proposals/<int:id>', methods=['PUT'])
@json
def update_proposal(id):
	current_proposal = Proposal.query.get_or_404(id)
	current_proposal.update_data(request.json)
	db.session.add(current_proposal)
	db.session.commit()

	return {}


@api.route('/proposals/<int:id>', methods=['DELETE'])
@json
def delete_proposal(id):
	current_proposal = Proposal.query.get_or_404(id)
	if current_proposal.user != g.user:
		response = {
			'status': 401,
			'error': 'unauthorized',
			'message': 'you are not allowed to delete this request'
		}

		return response, 401

	db.session.delete(current_proposal)
	db.session.commit()

	return {}