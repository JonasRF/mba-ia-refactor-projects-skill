import os
from datetime import datetime, timedelta, timezone

import jwt

from models.usuario import UsuarioModel
from controllers.constants import JWT_ALGORITHM, JWT_EXPIRATION_HORAS


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
        payload = {
            "sub": usuario["id"],
            "role": usuario["tipo"],
            "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HORAS),
        }
        token = jwt.encode(payload, os.environ["SECRET_KEY"], algorithm=JWT_ALGORITHM)
        return {"usuario": usuario, "token": token}
