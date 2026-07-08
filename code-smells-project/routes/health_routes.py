from flask import Blueprint, jsonify
from controllers.system_controller import SystemController

health_bp = Blueprint("health", __name__)

@health_bp.get("/health")
def health_check():
    try:
        resultado = SystemController.health()
        return jsonify(resultado), 200
    except Exception:
        return jsonify({"status": "erro", "detalhes": "Erro interno"}), 500

@health_bp.get("/")
def index():
    return jsonify({
        "mensagem": "Bem-vindo à API da Loja",
        "versao": "1.0.0",
        "endpoints": {
            "produtos": "/produtos",
            "usuarios": "/usuarios",
            "pedidos": "/pedidos",
            "login": "/login",
            "relatorios": "/relatorios/vendas",
            "health": "/health"
        }
    }), 200
