__all__ = [
	'index',
	'users',
	'requests',
	'proposals'
]

from flask import Blueprint

api = Blueprint('api', __name__)