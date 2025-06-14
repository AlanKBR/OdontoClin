from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

# Import db from extensions.py
from app.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"
    __bind_key__ = "users"  # Added to route queries for this model to the 'users' bind

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True, nullable=False)
    nome_completo = db.Column(db.String(128), nullable=False)
    cro = db.Column(
        db.String(20), unique=True, nullable=True
    )  # CRO agora é obrigatório para profissionais
    nome_profissional = db.Column(db.String(120), nullable=False)  # Professional name field
    password_hash = db.Column(db.String(256))  # Aumentado para 256
    cargo = db.Column(db.String(50), nullable=False, default="dentista")  # Novo campo para cargo
    is_active = db.Column(db.Boolean, default=True)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<User {self.username}>"
