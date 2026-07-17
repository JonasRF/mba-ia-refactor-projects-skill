import os
import secrets
from flask import Flask
from flask_cors import CORS
from database.connection import init_app
from routes.produto_routes import produto_bp
from routes.usuario_routes import usuario_bp
from routes.pedido_routes import pedido_bp
from routes.auth_routes import auth_bp
from routes.relatorio_routes import relatorio_bp
from routes.health_routes import health_bp


def create_app(config=None):
    app = Flask(__name__)

    secret_key = os.environ.get("SECRET_KEY")
    if not secret_key:
        secret_key = secrets.token_hex(32)
        os.environ["SECRET_KEY"] = secret_key
        print("WARNING: SECRET_KEY not set — using generated key. Set SECRET_KEY env var for production.")
    app.config["SECRET_KEY"] = secret_key
    app.config["DATABASE"] = os.environ.get("DATABASE_PATH", "loja.db")
    app.config["DEBUG"] = os.environ.get("FLASK_DEBUG", "false").lower() == "true"

    if config:
        app.config.update(config)

    CORS(app)
    init_app(app)

    app.register_blueprint(produto_bp)
    app.register_blueprint(usuario_bp)
    app.register_blueprint(pedido_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(relatorio_bp)
    app.register_blueprint(health_bp)

    return app


if __name__ == "__main__":
    application = create_app()
    print("=" * 50)
    print("SERVIDOR INICIADO")
    print("Rodando em http://localhost:5000")
    print("=" * 50)
    application.run(host="0.0.0.0", port=5000)
