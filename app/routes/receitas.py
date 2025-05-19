"""
Módulo com rotas relacionadas a receitas médicas.
"""

from flask import Blueprint, Response, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import receitas_db
from app.models.receita import Medicamento, ModeloReceita

receitas = Blueprint("receitas", __name__)


@receitas.route("/")
@login_required
def index() -> Response:
    """Página principal de receitas."""
    return render_template("receitas/index.html")


@receitas.route("/nova")
@login_required
def nova_receita() -> Response:
    """Página para criar nova receita."""
    return render_template("receitas/formulario_receita.html")


@receitas.route("/medicamentos")
@login_required
def listar_medicamentos() -> Response:
    """Lista todos os medicamentos cadastrados."""
    medicamentos = Medicamento.query.order_by(Medicamento.nome).all()
    return render_template("receitas/lista_medicamentos.html", medicamentos=medicamentos)


@receitas.route("/medicamentos/<int:medicamento_id>")
@login_required
def visualizar_medicamento(medicamento_id: int) -> Response:
    """Visualiza detalhes de um medicamento específico."""
    medicamento = Medicamento.query.get_or_404(medicamento_id)

    # Criando uma cópia dos dados para evitar problemas de perda de dados
    dados_medicamento = {
        "id": medicamento.id,
        "nome": medicamento.nome,
        "principio_ativo": medicamento.principio_ativo,
        "concentracao": medicamento.concentracao,
        "forma_farmaceutica": medicamento.forma_farmaceutica,
        "posologia_padrao": medicamento.posologia_padrao,
        "via_administracao": medicamento.via_administracao,
        "indicacoes": medicamento.indicacoes,
        "contraindicacoes": medicamento.contraindicacoes,
        "efeitos_colaterais": medicamento.efeitos_colaterais,
        "observacoes": medicamento.observacoes,
        "odontologico": medicamento.odontologico,
    }

    # Passa os dados do medicamento como um objeto para o template
    from types import SimpleNamespace

    medicamento_obj = SimpleNamespace(**dados_medicamento)

    return render_template("receitas/visualizar_medicamento.html", medicamento=medicamento_obj)


@receitas.route("/medicamentos/buscar", methods=["GET"])
@login_required
def buscar_medicamentos() -> Response:
    """Busca medicamentos por nome ou princípio ativo."""
    termo = request.args.get("termo", "")
    if termo:
        medicamentos = (
            Medicamento.query.filter(
                (Medicamento.nome.ilike(f"%{termo}%"))
                | (Medicamento.principio_ativo.ilike(f"%{termo}%"))
            )
            .order_by(Medicamento.nome)
            .all()
        )
    else:
        medicamentos = []

    # Se for uma solicitação AJAX, retorna JSON
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        result = []
        for med in medicamentos:
            result.append(
                {
                    "id": med.id,
                    "nome": med.nome,
                    "principio_ativo": med.principio_ativo,
                    "concentracao": med.concentracao,
                    "posologia_padrao": med.posologia_padrao,
                }
            )
        return jsonify(result)

    # Se não for AJAX, renderiza a página
    return render_template(
        "receitas/lista_medicamentos.html", medicamentos=medicamentos, termo_busca=termo
    )


@receitas.route("/modelos")
@login_required
def listar_modelos() -> Response:
    """Lista todos os modelos de receita do usuário atual."""
    modelos = ModeloReceita.query.filter_by(usuario_id=current_user.id).all()
    return render_template("receitas/modelos_receita.html", modelos=modelos)


@receitas.route("/modelos/salvar", methods=["POST"])
@login_required
def salvar_modelo() -> Response:
    """Salva um novo modelo de receita."""
    titulo = request.form.get("titulo")
    conteudo = request.form.get("conteudo")

    if not titulo or not conteudo:
        flash("Título e conteúdo são obrigatórios.", "danger")
        return redirect(url_for("receitas.listar_modelos"))

    modelo = ModeloReceita(titulo=titulo, conteudo=conteudo, usuario_id=current_user.id)

    receitas_db.session.add(modelo)
    receitas_db.session.commit()

    flash("Modelo de receita salvo com sucesso!", "success")
    return redirect(url_for("receitas.listar_modelos"))


@receitas.route("/modelos/<int:modelo_id>/visualizar")
@login_required
def visualizar_modelo(modelo_id: int) -> Response:
    """Visualiza um modelo de receita."""
    modelo = ModeloReceita.query.get_or_404(modelo_id)
    if modelo.usuario_id != current_user.id:
        flash("Você não tem permissão para acessar este modelo.", "danger")
        return redirect(url_for("receitas.listar_modelos"))

    # Criando uma cópia dos dados para evitar problemas de perda de dados
    dados_modelo = {
        "id": modelo.id,
        "titulo": modelo.titulo,
        "conteudo": modelo.conteudo,
        "usuario_id": modelo.usuario_id,
    }

    # Passa os dados do modelo como um objeto para o template
    from types import SimpleNamespace

    modelo_obj = SimpleNamespace(**dados_modelo)

    return render_template("receitas/visualizar_modelo.html", modelo=modelo_obj)


@receitas.route("/modelos/<int:modelo_id>/excluir", methods=["POST"])
@login_required
def excluir_modelo(modelo_id: int) -> Response:
    """Exclui um modelo de receita."""
    modelo = ModeloReceita.query.get_or_404(modelo_id)
    if modelo.usuario_id != current_user.id:
        flash("Você não tem permissão para excluir este modelo.", "danger")
        return redirect(url_for("receitas.listar_modelos"))

    receitas_db.session.delete(modelo)
    receitas_db.session.commit()

    flash("Modelo de receita excluído com sucesso!", "success")
    return redirect(url_for("receitas.listar_modelos"))
