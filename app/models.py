from datetime import datetime
from flask_login import UserMixin
from app import db, login
from enum import Enum as PyEnum
from sqlalchemy import Enum

class Status(PyEnum):
    PENDING = "Pending"
    IN_REVIEW = "In review"
    CLOSED = "Closed"

    def __str__(self):
        return f'{self.name}'

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    users = db.relationship('User', backref='group', lazy=True)
    tickets = db.relationship('Ticket', backref='group', lazy=True)

    def __repr__(self):
        return f'<Group {self.name}>'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))

    def __repr__(self):
        return f'<User {self.username}>'

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(Enum(Status), nullable=False, default=Status.PENDING)
    note = db.Column(db.Text, nullable=True)
    assigned_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    assigned_group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now())

    def __repr__(self):
        return f'<Ticket {self.id} - {self.status}>'
    

@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))