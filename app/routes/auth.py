from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from flask_wtf import FlaskForm

# Removed unused imports but left them commented for reference in case needed later
# from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

from app.extensions import db  # Reverted from ..extensions
from app.models.user import User  # Reverted from ..models.user

# Create a base form with CSRF disabled for all forms


class CSRFDisabledForm(FlaskForm):
    class Meta:
        csrf = False


auth = Blueprint("auth", __name__)

# Formulário de login


class LoginForm(CSRFDisabledForm):
    username = StringField("Nome de usuário", validators=[DataRequired()])
    password = PasswordField("Senha", validators=[DataRequired()])
    submit = SubmitField("Entrar")


# Formulário de cadastro


class RegistrationForm(CSRFDisabledForm):
    username = StringField("Nome de usuário", validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    nome_completo = StringField("Nome completo", validators=[DataRequired(), Length(max=128)])
    cargo = SelectField(
        "Cargo",
        choices=[
            ("dentista", "Dentista"),
            ("secretaria", "Secretária/Recepcionista"),
            ("admin", "Administrador"),
        ],
    )
    password = PasswordField("Senha", validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField(
        "Confirmar senha", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Cadastrar")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.dashboard"))
        flash("Nome de usuário ou senha incorretos", "danger")

    return render_template("auth/login.html", form=form)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu do sistema.", "info")
    return redirect(url_for("auth.login"))


@auth.route("/register", methods=["GET", "POST"])
@login_required
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Verifica se nome de usuário ou email já existem
        if User.query.filter_by(username=form.username.data).first():
            flash("Nome de usuário já existe", "danger")
            return render_template("auth/register.html", form=form)

        if User.query.filter_by(email=form.email.data).first():
            flash("Email já está cadastrado", "danger")
            return render_template("auth/register.html", form=form)

        # Cria novo usuário
        user = User(
            username=form.username.data,
            email=form.email.data,
            nome_completo=form.nome_completo.data,
            cargo=form.cargo.data,
        )
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash("Usuário cadastrado com sucesso!", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("auth/register.html", form=form)
