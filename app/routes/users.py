from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from wtforms import HiddenField, PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional

from app import extensions
from app.models.user import User

users = Blueprint("users", __name__)


# Formulário base com CSRF desabilitado
class CSRFDisabledForm(FlaskForm):
    class Meta:
        csrf = False


# Formulário para criar/editar usuário
class UserForm(CSRFDisabledForm):
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
    password = PasswordField("Senha", validators=[Optional(), Length(min=8)])
    confirm_password = PasswordField("Confirmar senha", validators=[EqualTo("password")])
    id = HiddenField("ID")
    submit = SubmitField("Salvar")


@users.route("/")
@login_required
def listar_usuarios():
    # Lista todos os usuários
    usuarios = extensions.users_db.query(User).all()
    return render_template("users/lista_usuarios.html", usuarios=usuarios)


@users.route("/novo", methods=["GET", "POST"])
@login_required
def novo_usuario():
    form = UserForm()

    if form.validate_on_submit():
        # Verifica se o nome de usuário já existe
        if extensions.users_db.query(User).filter_by(username=form.username.data).first():
            flash("Nome de usuário já existe", "danger")
            return render_template(
                "users/formulario_usuario.html", form=form, titulo="Novo Usuário"
            )

        # Verifica se o email já existe
        if extensions.users_db.query(User).filter_by(email=form.email.data).first():
            flash("Email já está cadastrado", "danger")
            return render_template(
                "users/formulario_usuario.html", form=form, titulo="Novo Usuário"
            )

        # Cria novo usuário
        novo_usuario = User(
            username=form.username.data,
            email=form.email.data,
            nome_completo=form.nome_completo.data,
            cargo=form.cargo.data,
        )

        # Definir a senha apenas se for fornecida
        if form.password.data:
            novo_usuario.set_password(form.password.data)
        else:
            flash("A senha é obrigatória para novos usuários", "danger")
            return render_template(
                "users/formulario_usuario.html", form=form, titulo="Novo Usuário"
            )

        extensions.users_db.add(novo_usuario)
        extensions.users_db.commit()

        flash("Usuário criado com sucesso!", "success")
        return redirect(url_for("users.listar_usuarios"))

    return render_template("users/formulario_usuario.html", form=form, titulo="Novo Usuário")


@users.route("/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_usuario(id):
    usuario = extensions.users_db.query(User).get(id)
    if usuario is None:
        abort(404)

    # Inicializa o formulário com os dados do usuário
    if request.method == "GET":
        form = UserForm(
            id=usuario.id,
            username=usuario.username,
            email=usuario.email,
            nome_completo=usuario.nome_completo,
            cargo=usuario.cargo,
        )
    else:
        form = UserForm()

    if form.validate_on_submit():
        # Verifica se o username já existe para outro usuário
        existing_user = (
            extensions.users_db.query(User).filter_by(username=form.username.data).first()
        )
        if existing_user and existing_user.id != usuario.id:
            flash("Nome de usuário já existe", "danger")
            return render_template(
                "users/formulario_usuario.html", form=form, titulo="Editar Usuário"
            )

        # Verifica se o email já existe para outro usuário
        existing_email = extensions.users_db.query(User).filter_by(email=form.email.data).first()
        if existing_email and existing_email.id != usuario.id:
            flash("Email já está cadastrado", "danger")
            return render_template(
                "users/formulario_usuario.html", form=form, titulo="Editar Usuário"
            )

        # Atualiza os dados do usuário
        usuario.username = form.username.data
        usuario.email = form.email.data
        usuario.nome_completo = form.nome_completo.data
        usuario.cargo = form.cargo.data

        # Atualiza a senha apenas se for fornecida
        if form.password.data:
            usuario.set_password(form.password.data)

        extensions.users_db.commit()
        flash("Usuário atualizado com sucesso!", "success")
        return redirect(url_for("users.listar_usuarios"))

    return render_template("users/formulario_usuario.html", form=form, titulo="Editar Usuário")


@users.route("/perfil", methods=["GET", "POST"])
@login_required
def meu_perfil():
    usuario = extensions.users_db.query(User).get(current_user.id)

    # Inicializa o formulário com os dados do usuário
    if request.method == "GET":
        form = UserForm(
            id=usuario.id,
            username=usuario.username,
            email=usuario.email,
            nome_completo=usuario.nome_completo,
            cargo=usuario.cargo,
        )
    else:
        form = UserForm()

    if form.validate_on_submit():
        # Verifica se o username já existe para outro usuário
        existing_user = (
            extensions.users_db.query(User).filter_by(username=form.username.data).first()
        )
        if existing_user and existing_user.id != usuario.id:
            flash("Nome de usuário já existe", "danger")
            return render_template("users/meu_perfil.html", form=form)

        # Verifica se o email já existe para outro usuário
        existing_email = extensions.users_db.query(User).filter_by(email=form.email.data).first()
        if existing_email and existing_email.id != usuario.id:
            flash("Email já está cadastrado", "danger")
            return render_template("users/meu_perfil.html", form=form)

        # Atualiza os dados do usuário
        usuario.username = form.username.data
        usuario.email = form.email.data
        usuario.nome_completo = form.nome_completo.data

        # O cargo não pode ser alterado pelo próprio usuário

        # Atualiza a senha apenas se for fornecida
        if form.password.data:
            usuario.set_password(form.password.data)

        extensions.users_db.commit()
        flash("Perfil atualizado com sucesso!", "success")
        return redirect(url_for("users.meu_perfil"))

    return render_template("users/meu_perfil.html", form=form)


@users.route("/visualizar/<int:id>")
@login_required
def visualizar_usuario(id):
    usuario = extensions.users_db.query(User).get(id)
    if usuario is None:
        abort(404)
    return render_template("users/visualizar_usuario.html", usuario=usuario)


@users.route("/excluir/<int:id>", methods=["POST"])
@login_required
def excluir_usuario(id):
    usuario = extensions.users_db.query(User).get(id)
    if usuario is None:
        abort(404)

    # Impede a exclusão do próprio usuário logado
    if usuario.id == current_user.id:
        flash("Você não pode excluir seu próprio usuário!", "danger")
        return redirect(url_for("users.listar_usuarios"))

    # Remove o usuário do banco de dados
    extensions.users_db.delete(usuario)
    extensions.users_db.commit()

    flash("Usuário excluído com sucesso!", "success")
    return redirect(url_for("users.listar_usuarios"))
