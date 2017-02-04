from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask import url_for
from main import db
from main.errors import ValidationError
from main.models.base import TimestampMixin

class User(db.Model, TimestampMixin):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True)
	password_hash = db.Column(db.String(128))
	email = db.Column(db.String(128), index=True)
	photo_url = db.Column(db.String(256), index=True)
	requests = db.relationship('Request', backref='user', lazy='dynamic')
	proposals = db.releationship('Proposal', backref='user', lazy='dynamic')


	def set_password_hash(self, password):
		self.password_hash = generate_password_hash(password)


	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)


	def generate_auth_token(self, expires_in=3600):
		s = Serializer(current_app.config['SECRET_KEY'], expires_in=expires_in)
		return s.dumps({'id': self.id}).decode('utf-8')


	def get_url(self):
		return url_for('api.get_user', id=self.id, _external=True)


	def export_data(self):
		return {
			'self_url': self.get_url(),
			'username': self.username,
			'email': self.email,
			'photo_url': self.photo_url
		}

	def import_data(self, data):
		try:
			self.username = data['username']
			self.email = data['email']
			self.photo_url = data['photo_url']
			self.set_password_hash(data['password'])
		except KeyError as e:
			raise ValidationError('Invalid user: missing ' + e.args[0])

		return self

	def update_data(self, data):
		fields = ['username', 'email', 'photo_url']
		for field in fields:
			if field in data:
				setattr(self, field, data[field])

		if 'password' in data:
			self.set_password_hash(data['password'])
		
		return self

	@staticmethod
	def verify_auth_token(token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return None

		return User.query.get(data['id'])
