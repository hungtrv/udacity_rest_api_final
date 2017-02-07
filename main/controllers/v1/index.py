from . import api
from main.decorators import json


@api.route('/')
@json
def index():
    response = {
        'status': 200,
        'error': 'Not Found',
        'message': 'Welcome to Meet N Eat!'
    }

    return response
