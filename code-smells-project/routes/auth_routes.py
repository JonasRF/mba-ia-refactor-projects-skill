from flask import Blueprint, request, jsonify
from controllers.usuario_controller import UsuarioController

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/login")
def login():
    dados = request.get_json(silent=True) or {}
    email = dados.get("email", "")
    senha = dados.get("senha", "")
    try:
        usuario = UsuarioController.autenticar(email, senha)
        return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}), 200
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    except PermissionError as e:
        return jsonify({"erro": str(e), "sucesso": False}), 401
