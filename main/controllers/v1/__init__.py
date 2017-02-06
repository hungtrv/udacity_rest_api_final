__all__ = [
	'index',
	'users',
	'requests',
	'proposals',
	'dates'
]

from flask import Blueprint

api = Blueprint('api', __name__)