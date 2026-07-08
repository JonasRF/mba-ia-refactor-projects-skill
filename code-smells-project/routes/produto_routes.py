from flask import Blueprint, request, jsonify
from controllers.produto_controller import ProdutoController

produto_bp = Blueprint("produtos", __name__, url_prefix="/produtos")


def _parse_produto_body(dados: dict) -> dict:
    for campo in ["nome", "preco", "estoque"]:
        if campo not in dados:
            raise ValueError(f"Campo obrigatório ausente: {campo}")
    try:
        return {
            "nome": str(dados["nome"]),
            "descricao": str(dados.get("descricao", "")),
            "preco": float(dados["preco"]),
            "estoque": int(dados["estoque"]),
            "categoria": str(dados.get("categoria", "geral")),
        }
    except (TypeError, ValueError) as e:
        raise ValueError(f"Tipo de campo inválido: {e}")


def _parse_float_param(valor, nome: str):
    if valor is None:
        return None
    try:
        return float(valor)
    except (TypeError, ValueError):
        raise ValueError(f"'{nome}' deve ser numérico, recebido: '{valor}'")


@produto_bp.get("/listar")
def listar_produtos():
    return jsonify({"dados": ProdutoController.listar(), "sucesso": True}), 200


@produto_bp.get("/busca")
def buscar_produtos():
    try:
        preco_min = _parse_float_param(request.args.get("preco_min"), "preco_min")
        preco_max = _parse_float_param(request.args.get("preco_max"), "preco_max")
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400

    resultados = ProdutoController.buscar_com_filtros(
        termo=request.args.get("q", ""),
        categoria=request.args.get("categoria"),
        preco_min=preco_min,
        preco_max=preco_max
    )
    return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200


@produto_bp.get("/<int:produto_id>")
def buscar_produto(produto_id: int):
    try:
        produto = ProdutoController.buscar(produto_id)
        return jsonify({"dados": produto, "sucesso": True}), 200
    except LookupError as e:
        return jsonify({"erro": str(e)}), 404

@produto_bp.post("/criar")
def criar_produto():
    dados = request.get_json(silent=True) or {}
    try:
        campos = _parse_produto_body(dados)
        resultado = ProdutoController.criar(**campos)
        return jsonify({"dados": resultado, "sucesso": True, "mensagem": "Produto criado"}), 201
    except LookupError as e:
        return jsonify({"erro": str(e)}), 404
    except (TypeError, ValueError) as e:
        return jsonify({"erro": str(e)}), 400

@produto_bp.put("/<int:produto_id>")
def atualizar_produto(produto_id: int):
    dados = request.get_json(silent=True) or {}
    try:
        campos = _parse_produto_body(dados)
        ProdutoController.atualizar(produto_id, **campos)
        return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200
    except LookupError as e:
        return jsonify({"erro": str(e)}), 404
    except (TypeError, ValueError) as e:
        return jsonify({"erro": str(e)}), 400

@produto_bp.delete("/<int:produto_id>")
def deletar_produto(produto_id: int):
    try:
        ProdutoController.deletar(produto_id)
        return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200
    except LookupError as e:
        return jsonify({"erro": str(e)}), 404
