# models/port.py
from . import db

class Port(db.Model):
    __tablename__ = 'ports'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'country': self.country,
            'location': [self.latitude, self.longitude]
        }

    def __repr__(self):
        return f"<Port {self.name} ({self.country})>"