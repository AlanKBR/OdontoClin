from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# Definição das extensões
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

# Estas variáveis serão atualizadas com as sessões específicas após inicialização
# Isto permite que o código existente continue funcionando com mínimas modificações
users_db = None
pacientes_db = None
tratamentos_db = None
receitas_db = None
