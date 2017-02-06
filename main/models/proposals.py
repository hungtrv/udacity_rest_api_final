from flask import url_for
from main import db
from main.errors import ValidationError
from main.models.base import TimestampMixin

class Proposal(db.Model, TimestampMixin):
	__tablename__ = 'proposals'
	id = db.Column(db.Integer, primary_key=True)
	request_id = db.Column(db.Integer, db.ForeignKey('requests.id'), index=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	accepted = db.Column(db.Boolean, default=False)


	def get_url(self):
		return url_for('api.get_proposal', id=self.id, _external=True)


	def export_data(self):
		return {
			'self_url': self.get_url(),
			'user_url': self.user.get_url(),
			'request_url': self.request.get_url(),
			'accepted': self.accepted,
		}


	def import_data(self, data):
		try:
			pass
		except KeyError as e:
			raise ValidationError('Invalid user: missing ' + e.args[0])

		return self


	def update_data(self, data):
		fields = ['accepted']
		for field in fields:
			if field in data:
				setattr(self, field, data[field])
		
		return self