from flask import url_for
from main import db
from main.errors import ValidationError
from main.models.base import TimestampMixin

# TODO: Add date/time to a Date


class Date(db.Model, TimestampMixin):
    __tablename__ = 'dates'
    id = db.Column(db.Integer, primary_key=True)
    proposal_id = db.Column(
        db.Integer, db.ForeignKey('proposals.id'), index=True)
    #meal_date = db.Column(db.DateTime)
    restaurant_name = db.Column(db.String(256), index=True)
    restaurant_address = db.Column(db.String(256), index=True)

    def get_url(self):
        return url_for('api.get_date', id=self.id, _external=True)

    def export_data(self):
        return {
            'self_url': self.get_url(),
            'request_user_url': url_for('api.get_user', id=self.proposal.request.user.id, _exteral=True),
            'proposal_user_url': url_for('api.get_user', id=self.proposal.user.id, _external=True),
            #'meal_date': self.meal_date,
            'meal_time': self.proposal.request.meal_time,
            'restaurant_name': self.restaurant_name,
            'restaurant_address': self.restaurant_address
        }

    def import_data(self, data):
        try:
            pass
        except KeyError as e:
            raise ValidationError('Invalid user: missing ' + e.args[0])

        return self

    def update_data(self, data):
        fields = ['restaurant_name', 'restaurant_address']
        for field in fields:
            if field in data:
                setattr(self, field, data[field])

        return self
