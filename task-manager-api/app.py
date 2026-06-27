import os
from flask import Flask
from flask_cors import CORS
from database import db
from config import Config
from routes.health_routes import health_bp
from routes.task_routes import task_bp
from routes.user_routes import user_bp
from routes.report_routes import report_bp
from routes.category_routes import category_bp


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    if config:
        app.config.update(config)

    CORS(app)
    db.init_app(app)

    app.register_blueprint(health_bp)
    app.register_blueprint(task_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(category_bp)

    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    application = create_app()
    application.run(
        debug=application.config['DEBUG'],
        host='0.0.0.0',
        port=int(os.environ.get('PORT', '5000')),
    )
