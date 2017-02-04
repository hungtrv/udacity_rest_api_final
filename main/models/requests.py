from flask import url_for
from main import db
from main.errors import ValidationError
from main.models.base import TimestampMixin

class Request(db.Model, TimestampMixin):
	__tablename__ = 'requests'
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	meal_type = db.Column(db.String(64), index=True) 
	location_string = db.Column(db.String(128), index=True)
	meal_time = db.Column(db.String(32), index=True)
	latitude = db.Column(db.String(32))
	longitude = db.Column(db.String(32))
	filled = db.Column(db.Boolean)
	proposals = db.relationship('Proposal', backref='request', lazy='dynamic')

	def get_url(self):
		return url_for('api.get_request', id=self.id, _external=True)


	def export_data(self):
		return {
			'self_url': self.get_url(),
			'user_url': self.user.get_url(),
			'meal_type': self.meal_type,
			'location_string': self.location_string,
			'filled': self.filled,
			'proposals_url': url_for('api.get_request_proposals', id=self.id, _external=True)
		}

	def import_data(self, data):
		try:
			self.meal_type = data['meal_type']
			self.location_string = data['location_string']
			self.meal_time = data['meal_time']
		except KeyError as e:
			raise ValidationError('Invalid user: missing ' + e.args[0])

		return self

	def update_data(self, data):
		fields = ['meal_type', 'location_string', 'meal_time', 'latitude', 'longitude', 'filled']
		for field in fields:
			if field in data:
				setattr(self, field, data[field])
		
		return self