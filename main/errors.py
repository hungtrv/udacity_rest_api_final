from main import app
from main.decorators import json

from flask import jsonify



class ValidationError(ValueError):
    pass


@app.errorhandler(ValidationError)
@json
def bad_request(e):
    """
            Handling invalid data in POST/PUT requests
    """
    response = {
            'status': 400, 
            'error': 'bad request', 
            'message': e.args[0]
        }
    

    return response, 400


@app.errorhandler(404)
@json
def not_found(e):
    """
            Handling 404 page not found
    """
    response = {
        'status': 404,
        'error': 'not found',
        'message': 'invalid resource URI'
    }

    return response, 404


@app.errorhandler(405)
@json
def method_not_supported(e):
    response = {
        'status': 405,
        'error': 'method not supported',
        'message': 'the method is not supported'
    }

    return response, 405


@app.errorhandler(500)
@json
def internal_server_error(e):
    response = {
        'status': 500,
        'error': 'internal server error',
        'message': e.args[0]
    }

    return response, 500