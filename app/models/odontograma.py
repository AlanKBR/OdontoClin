"""
Modelo para o Odontograma.
"""

from datetime import datetime

from app.extensions import db


class Odontograma(db.Model):
    """Representa um odontograma de um paciente."""

    __tablename__ = "odontogramas"
    __bind_key__ = "pacientes"  # Explicitly bind Odontograma to the 'pacientes' database

    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey("pacientes.id"), nullable=False)
    dados = db.Column(db.Text, nullable=False)  # Armazena os dados do odontograma em formato JSON
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    criado_por = db.Column(db.Integer, nullable=False)  # Still store the user ID

    # Relacionamentos
    paciente = db.relationship("Paciente", backref=db.backref("odontogramas", lazy="dynamic"))
    usuario = db.relationship(
        "User",
        primaryjoin="foreign(Odontograma.criado_por) == remote(User.id)",
        backref=db.backref("odontogramas_criados", lazy="dynamic"),
    )

    def __repr__(self):
        return f"<Odontograma {self.id} do Paciente {self.paciente_id}>"
