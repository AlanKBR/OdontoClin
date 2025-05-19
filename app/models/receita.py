"""
Este módulo define os modelos relacionados a receitas médicas.
"""

from sqlalchemy import Boolean, Column, Integer, String, Text

from app.extensions import db


class Medicamento(db.Model):
    """
    Modelo para representar medicamentos que podem ser prescritos.

    Atributos:
        id (int): Identificador único do medicamento
        nome (str): Nome do medicamento
        principio_ativo (str): Princípio ativo do medicamento
        concentracao (str): Concentração do medicamento (ex: 500mg, 10mg/ml)
        forma_farmaceutica (str): Forma farmacêutica (comprimido, solução, etc)
        posologia_padrao (str): Instruções padrão de posologia
        via_administracao (str): Via de administração (oral, tópica, etc)
        indicacoes (str): Indicações comuns para o medicamento
        contraindicacoes (str): Contraindicações do medicamento
        efeitos_colaterais (str): Efeitos colaterais comuns
        observacoes (str): Observações adicionais
        odontologico (bool): Indica se é um medicamento comumente usado em odontologia
    """

    __tablename__ = "medicamentos"
    __bind_key__ = "receitas"

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False, index=True)
    principio_ativo = Column(String(100), nullable=False)
    concentracao = Column(String(50))
    forma_farmaceutica = Column(String(50))
    posologia_padrao = Column(Text, nullable=False)
    via_administracao = Column(String(30))
    indicacoes = Column(Text)
    contraindicacoes = Column(Text)
    efeitos_colaterais = Column(Text)
    observacoes = Column(Text)
    odontologico = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Medicamento {self.nome}>"


class ModeloReceita(db.Model):
    """
    Modelo para representar modelos de texto de receitas salvas pelo usuário.

    Atributos:
        id (int): Identificador único do modelo
        titulo (str): Título do modelo de receita
        conteudo (str): Conteúdo do modelo de receita
        usuario_id (int): ID do usuário que criou o modelo
    """

    __tablename__ = "modelos_receita"
    __bind_key__ = "receitas"

    id = Column(Integer, primary_key=True)
    titulo = Column(String(100), nullable=False)
    conteudo = Column(Text, nullable=False)
    usuario_id = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<ModeloReceita {self.titulo}>"
