from app import create_app, extensions
from app.models.user import User


def criar_usuario_admin(username, email, nome_completo, senha):
    """Cria um usuário administrador inicial para o sistema."""
    app = create_app()

    with app.app_context():
        # Verificar se já existe um usuário com este username
        usuario_existente = extensions.users_db.query(User).filter_by(username=username).first()
        if usuario_existente:
            print(f"AVISO: Já existe um usuário com o username '{username}'")
            return

        # Criar o usuário administrador
        usuario = User(username=username, email=email, nome_completo=nome_completo, cargo="admin")
        usuario.set_password(senha)

        extensions.users_db.add(usuario)
        extensions.users_db.commit()
        print(f"Usuário administrador '{username}' criado com sucesso!")


if __name__ == "__main__":
    import getpass

    print("-" * 60)
    print("CRIAÇÃO DE USUÁRIO ADMINISTRADOR PARA ODONTOCLINIC")
    print("-" * 60)

    username = input("Username: ")
    email = input("Email: ")
    nome_completo = input("Nome completo: ")
    senha = getpass.getpass("Senha: ")
    confirmacao_senha = getpass.getpass("Confirme a senha: ")

    if senha != confirmacao_senha:
        print("ERRO: As senhas não coincidem!")
    elif len(senha) < 8:
        print("ERRO: A senha deve ter pelo menos 8 caracteres!")
    else:
        criar_usuario_admin(username, email, nome_completo, senha)
