import os
from datetime import date, datetime  # Add date for date filtering
from typing import Union  # Add Union for Python < 3.10 compatibility if needed

from flask import Flask, render_template
from markupsafe import Markup

from app.models.user import User

# Import blueprints and models at the top level
from app.routes.auth import auth
from app.routes.cro import cro_bp  # Adicionando o novo blueprint de CRO
from app.routes.main import main
from app.routes.pacientes import pacientes
from app.routes.receitas import receitas  # Adicionando o novo blueprint de receitas
from app.routes.tratamentos import tratamentos
from app.routes.users import users

# Import extensions from the new extensions.py file
from .extensions import db, login_manager, migrate
from .multidb import multidb


def create_app() -> Flask:
    app = Flask(__name__)

    # Enable Jinja2 'do' extension
    app.jinja_env.add_extension("jinja2.ext.do")

    # Configuração do banco de dados
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "chave-secreta-temporaria")

    # Diretório instance
    instance_path = os.path.abspath(os.path.join(app.root_path, "..", "instance"))

    # Configuração dos bancos de dados separados
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///app.db")
    app.config["USERS_DATABASE_URI"] = os.environ.get(
        "USERS_DATABASE_URI", f"sqlite:///{os.path.join(instance_path, 'users.db')}"
    )
    app.config["PACIENTES_DATABASE_URI"] = os.environ.get(
        "PACIENTES_DATABASE_URI", f"sqlite:///{os.path.join(instance_path, 'pacientes.db')}"
    )
    app.config["TRATAMENTOS_DATABASE_URI"] = os.environ.get(
        "TRATAMENTOS_DATABASE_URI", f"sqlite:///{os.path.join(instance_path, 'tratamentos.db')}"
    )
    app.config["RECEITAS_DATABASE_URI"] = os.environ.get(
        "RECEITAS_DATABASE_URI", f"sqlite:///{os.path.join(instance_path, 'receitas.db')}"
    )

    # Inicializa extensões
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_BINDS"] = {
        "users": app.config["USERS_DATABASE_URI"],
        "pacientes": app.config["PACIENTES_DATABASE_URI"],
        "tratamentos": app.config["TRATAMENTOS_DATABASE_URI"],
        "receitas": app.config["RECEITAS_DATABASE_URI"],
    }

    # Disable CSRF protection completely
    app.config["WTF_CSRF_ENABLED"] = False

    # Inicializa os bancos de dados
    db.init_app(app)  # Initialize the main db instance first
    migrate.init_app(app, db)

    # Inicializa sistema de múltiplos bancos de dados, passing the main db instance
    multidb.init_app(app, db_instance=db)  # Pass the db instance from extensions

    # Update the placeholder variables in extensions.py
    from . import extensions

    extensions.users_db = multidb.get_session("users")
    extensions.pacientes_db = multidb.get_session("pacientes")
    extensions.tratamentos_db = multidb.get_session("tratamentos")
    extensions.receitas_db = multidb.get_session("receitas")

    # Configuração do login
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Por favor, faça login para acessar esta página."
    login_manager.login_message_category = "info"

    # Registra os blueprints
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(main, url_prefix="/")
    app.register_blueprint(pacientes, url_prefix="/pacientes")
    app.register_blueprint(tratamentos, url_prefix="/tratamentos")
    app.register_blueprint(users, url_prefix="/users")
    app.register_blueprint(receitas, url_prefix="/receitas")  # Registro do blueprint de receitas
    app.register_blueprint(cro_bp, url_prefix="/cro")  # Registro do blueprint de CRO

    # Custom Jinja filter for date formatting
    def format_date_filter(value: Union[datetime, date], format: str = "%d/%m/%Y") -> str:
        if value and isinstance(value, (datetime, date)):
            return value.strftime(format)
        return str(value)

    app.jinja_env.filters["date"] = format_date_filter

    @login_manager.user_loader
    def load_user(user_id: str) -> Union[User, None]:  # Assuming User model or None
        return User.query.get(int(user_id))

    # Adiciona função personalizada ao contexto Jinja
    app.jinja_env.globals.update(csp_nonce=lambda: Markup(""))

    # Registra função de erro 404
    @app.errorhandler(404)
    def page_not_found(e: Exception) -> tuple[str, int]:  # Or specific exception type
        return render_template("404.html"), 404

    # Registra função de erro 500
    @app.errorhandler(500)
    def internal_server_error(e: Exception) -> tuple[str, int]:  # Or specific exception type
        return render_template("500.html"), 500

    @app.template_filter("currency")
    def _jinja2_filter_currency(
        value: Union[float, int, None],
    ) -> str:  # Assuming value is numeric or None
        if value is None:
            return "R$ 0,00"
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    return app
