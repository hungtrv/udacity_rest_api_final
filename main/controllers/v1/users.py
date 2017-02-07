from flask import request

from . import api
from main import db
from main.errors import ValidationError
from main.models.users import User

from main.decorators import json
from main.decorators import paginate


@api.route('/users/', methods=['GET'])
@json
@paginate('users')
def get_users():
    return User.query


@api.route('/users/', methods=['POST'])
@json
def add_user():
    try:
        username = request.json['username']
        if User.query.filter_by(username=username).first():
            raise ValidationError('Username already existed!')
    except KeyError as e:
        raise ValidationError('Invalid user info: missing ' + e.args[0])
    user = User()
    user.import_data(request.json)
    db.session.add(user)
    db.session.commit()

    return {}, 201, {'Location': user.get_url()}


@api.route('/users/<int:id>', methods=['GET'])
@json
def get_user(id):
    return User.query.get_or_404(id).export_data()


@api.route('/users/<int:id>', methods=['PUT'])
@json
def edit_user(id):
    user = User.query.get_or_404(id)
    user.update_data(request.json)
    db.session.add(user)
    db.session.commit()

    return {}


@api.route('/users/<int:id>', methods=['DELETE'])
@json
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()

    return {}
