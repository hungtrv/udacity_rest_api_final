from flask import request
from flask import g

from . import api
from main import db
from main.models.requests import Request

from main.decorators import json
from main.decorators import paginate


@api.route('/requests/', methods=['GET'])
@json
@paginate('requests')
def get_requests():
    return Request.query


@api.route('/requests/<int:id>', methods=['GET'])
@json
def get_request(id):
    return Request.query.get_or_404(id).export_data()


@api.route('/requests/', methods=['POST'])
@json
def add_request():
    new_request = Request(user=g.user)
    new_request.import_data(request.json)
    db.session.add(new_request)
    db.session.commit()

    return {}, 201, {'Location': new_request.get_url()}


@api.route('/requests/<int:id>', methods=['PUT'])
@json
def update_request(id):
    tmp_request = Request.query.get_or_404(id)
    if tmp_request.user != g.user:
        response = {
            'status': 401,
            'error': 'unauthorized',
            'message': 'you are not allowed to change this request'
        }

        return response, 401

    tmp_request.import_data(request.json)
    db.session.add(tmp_request)
    db.session.commit()

    return {}


@api.route('/requests/<int:id>', methods=['DELETE'])
@json
def delete_request(id):
    tmp_request = Request.query.get_or_404(id)
    if tmp_request.user != g.user:
        response = {
            'status': 401,
            'error': 'unauthorized',
            'message': 'you are not allowed to delete this request'
        }

        return response, 401

    db.session.delete(tmp_request)
    db.session.commit()

    return {}
