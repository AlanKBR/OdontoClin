"""
Script para criar as tabelas no banco de dados de receitas.
"""

import os
import sys

from sqlalchemy import inspect

from app import create_app
from app.extensions import db
from app.models.receita import Medicamento, ModeloReceita

# Adiciona o diretório raiz ao path para que os imports funcionem
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


def criar_tabelas() -> None:
    """Cria as tabelas no banco de dados se não existirem."""
    app = create_app()
    with app.app_context():
        # Verifica se as tabelas já existem
        engine = db.get_engine(app, bind="receitas")
        inspector = inspect(engine)

        if "medicamentos" not in inspector.get_table_names():
            # Cria as tabelas manualmente
            Medicamento.__table__.create(bind=engine)
            print("Tabela 'medicamentos' criada com sucesso!")
        else:
            print("Tabela 'medicamentos' já existe.")

        if "modelos_receita" not in inspector.get_table_names():
            ModeloReceita.__table__.create(bind=engine)
            print("Tabela 'modelos_receita' criada com sucesso!")
        else:
            print("Tabela 'modelos_receita' já existe.")


if __name__ == "__main__":
    criar_tabelas()
