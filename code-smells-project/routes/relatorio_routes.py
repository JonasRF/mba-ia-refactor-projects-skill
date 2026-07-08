from flask import Blueprint, jsonify
from controllers.relatorio_controller import RelatorioController

relatorio_bp = Blueprint("relatorios", __name__, url_prefix="/relatorios")

@relatorio_bp.get("/vendas")
def relatorio_vendas():
    return jsonify({"dados": RelatorioController.vendas(), "sucesso": True}), 200
