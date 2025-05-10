import os

from flask import Flask
from markupsafe import Markup  # Changed from jinja2 to markupsafe

from app.models.user import User

# Import blueprints and models at the top level
from app.routes.auth import auth
from app.routes.main import main
from app.routes.pacientes import pacientes
from app.routes.tratamentos import tratamentos

# Import extensions from the new extensions.py file
from .extensions import db, login_manager, migrate


def create_app():
    app = Flask(__name__)

    # Configuração do banco de dados
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "chave-secreta-temporaria")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///app.db")
    # Inicializa extensões
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Disable CSRF protection completely
    app.config["WTF_CSRF_ENABLED"] = False

    db.init_app(app)
    migrate.init_app(app, db)

    # Configuração do login
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Por favor, faça login para acessar esta página."
    login_manager.login_message_category = "info"  # Registra os blueprints

    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(main, url_prefix="/")
    app.register_blueprint(pacientes, url_prefix="/pacientes")
    app.register_blueprint(tratamentos, url_prefix="/tratamentos")

    # Inicializa o user_loader do Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Registra filtros personalizados do Jinja
    @app.template_filter("nl2br")
    def nl2br(value):
        if not value:
            return ""
        return Markup(value.replace("\n", "<br>"))

    # Cria tabelas do banco de dados
    with app.app_context():
        db.create_all()

    return app
