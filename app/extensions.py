from flask_login import LoginManager
from flask_mobility import Mobility
from flask_sqlalchemy import SQLAlchemy

# Definição das extensões
db = SQLAlchemy()
login_manager = LoginManager()
mobility = Mobility()

# Estas variáveis serão atualizadas com as sessões específicas após inicialização
# Isto permite que o código existente continue funcionando com mínimas modificações
users_db = None
pacientes_db = None
tratamentos_db = None
receitas_db = None
