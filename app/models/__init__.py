# filepath: a:\programa\prototipo\app\models\__init__.py
# This file makes Python treat the directory as a package.

# Importa todos os modelos para garantir que eles sejam carregados
from app.models import odontograma, paciente, tratamento, user  # noqa

# Exportar classes importantes para facilitar a importação
from app.models.odontograma import Odontograma  # noqa
from app.models.paciente import (  # noqa
    Anamnese,
    Ficha,
    Financeiro,
    Historico,
    Paciente,
    PlanoTratamento,
    Procedimento,
)
from app.models.tratamento import CategoriaTratamento, Tratamento  # noqa
from app.models.user import User  # noqa
