__all__ = [
	'index',
	'users',
	'requests'
]

from flask import Blueprint

api = Blueprint('api', __name__)