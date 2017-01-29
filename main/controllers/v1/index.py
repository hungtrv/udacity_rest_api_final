from . import api

@api.route('/')
def index():
	return "<H1>Meat N' Eat Version 1.0</H1>"