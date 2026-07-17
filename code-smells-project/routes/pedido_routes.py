from flask import Blueprint, request, jsonify
from controllers.pedido_controller import PedidoController
from routes.auth_middleware import require_auth

pedido_bp = Blueprint("pedidos", __name__, url_prefix="/pedidos")
_controller = PedidoController()

@pedido_bp.post("/criar")
@require_auth
def criar_pedido():
    dados = request.get_json(silent=True) or {}
    try:
        resultado = _controller.criar(
            usuario_id=dados.get("usuario_id"),
            itens=dados.get("itens", [])
        )
        return jsonify({"dados": resultado, "sucesso": True, "mensagem": "Pedido criado com sucesso"}), 201
    except LookupError as e:
        return jsonify({"erro": str(e)}), 404
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400

@pedido_bp.get("/listar")
@require_auth
def listar_todos_pedidos():
    return jsonify({"dados": _controller.listar_todos(), "sucesso": True}), 200

@pedido_bp.get("/usuario/<int:usuario_id>")
def listar_pedidos_usuario(usuario_id: int):
    return jsonify({"dados": _controller.listar_por_usuario(usuario_id), "sucesso": True}), 200

@pedido_bp.put("/<int:pedido_id>/status")
@require_auth
def atualizar_status_pedido(pedido_id: int):
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "Body JSON obrigatório"}), 400
    try:
        _controller.atualizar_status(pedido_id, dados.get("status", ""))
        return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
