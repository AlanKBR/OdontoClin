from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

# Import db from extensions.py
from app.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"
    __bind_key__ = "users"  # Added to route queries for this model to the 'users' bind

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    nome_completo = db.Column(db.String(128))
    cargo = db.Column(db.String(64))  # Dentista, Secretária, etc.

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
