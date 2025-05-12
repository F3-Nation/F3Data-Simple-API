from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Org(db.Model):
    __tablename__ = 'orgs'
    id = db.Column(db.Integer, primary_key=True)
    org_type = db.Column(db.String, nullable=False)

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
