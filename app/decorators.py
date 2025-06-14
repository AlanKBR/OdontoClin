"""
Decoradores personalizados para o sistema OdontoClinic
"""

from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user


def admin_required(f):
    """
    Decorador que requer que o usuário tenha cargo 'admin' para acessar a rota.
    Deve ser usado após o decorador @login_required.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))

        if current_user.cargo != "admin":
            flash(
                "Acesso negado. Apenas administradores podem acessar esta funcionalidade.", "error"
            )
            return redirect(url_for("main.dashboard"))

        return f(*args, **kwargs)

    return decorated_function
