from flask import Blueprint, request, jsonify
from controllers.usuario_controller import UsuarioController

usuario_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")

@usuario_bp.get("/listar")
def listar_usuarios():
    return jsonify({"dados": UsuarioController.listar(), "sucesso": True}), 200

@usuario_bp.get("/<int:usuario_id>")
def buscar_usuario(usuario_id: int):
    try:
        usuario = UsuarioController.buscar(usuario_id)
        return jsonify({"dados": usuario, "sucesso": True}), 200
    except LookupError as e:
        return jsonify({"erro": str(e)}), 404

@usuario_bp.post("/criar")
def criar_usuario():
    dados = request.get_json(silent=True) or {}
    nome = dados.get("nome", "")
    email = dados.get("email", "")
    senha = dados.get("senha", "")
    try:
        resultado = UsuarioController.criar(nome, email, senha)
        return jsonify({"dados": resultado, "sucesso": True}), 201
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
