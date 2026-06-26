from models.usuario import UsuarioModel


class UsuarioController:

    @staticmethod
    def listar() -> list:
        return UsuarioModel.get_todos()

    @staticmethod
    def buscar(usuario_id: int) -> dict:
        usuario = UsuarioModel.get_por_id(usuario_id)
        if not usuario:
            raise LookupError("Usuário não encontrado")
        return usuario

    @staticmethod
    def criar(nome: str, email: str, senha: str) -> dict:
        if not nome or not email or not senha:
            raise ValueError("Nome, email e senha são obrigatórios")
        usuario_id = UsuarioModel.criar(nome, email, senha)
        return {"id": usuario_id}

    @staticmethod
    def autenticar(email: str, senha: str) -> dict:
        if not email or not senha:
            raise ValueError("Email e senha são obrigatórios")
        usuario = UsuarioModel.autenticar(email, senha)
        if not usuario:
            raise PermissionError("Email ou senha inválidos")
        return usuario
