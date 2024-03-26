from extensions import db, bcrypt
from flask_login import UserMixin


class User(UserMixin, db.Model):

    id = db.Column(db.Integer, unique=True, primary_key=True)
    username = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(254), unique=True, nullable=False)
    password = db.Column(db.String(30), nullable=False)
    session_token = db.Column(db.String(100), unique=True, nullable=True)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def get_id(self):
        return self.session_token


class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Float, nullable=False)
    content = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'Lesson ID: {self.id} time spent:{self.time}, content: {self.content}'


# TODO: add user id linked with timeleft
class TimeLeft(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time_left = db.Column(db.Float, nullable=False)
