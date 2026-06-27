from flask import Blueprint, jsonify
import datetime

health_bp = Blueprint('health', __name__)


@health_bp.route('/')
def index():
    return jsonify({'message': 'Task Manager API', 'version': '1.0'}), 200


@health_bp.route('/health')
def health():
    return jsonify({'status': 'ok', 'timestamp': str(datetime.datetime.now())}), 200
