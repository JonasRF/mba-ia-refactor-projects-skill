from flask import Blueprint, request, jsonify
from controllers.user_controller import UserController
from controllers.exceptions import ConflictError

user_bp = Blueprint('users', __name__)


@user_bp.route('/users', methods=['GET'])
def get_users():
    return jsonify(UserController.get_all()), 200


@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        return jsonify(UserController.get_by_id(user_id)), 200
    except LookupError as e:
        return jsonify({'error': str(e)}), 404


@user_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    try:
        user = UserController.create(
            name=data.get('name', ''),
            email=data.get('email', ''),
            password=data.get('password', ''),
            role=data.get('role', 'user'),
        )
        return jsonify(user), 201
    except ConflictError as e:
        return jsonify({'error': str(e)}), 409
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    try:
        return jsonify(UserController.update(user_id, data)), 200
    except LookupError as e:
        return jsonify({'error': str(e)}), 404
    except ConflictError as e:
        return jsonify({'error': str(e)}), 409
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        UserController.delete(user_id)
        return jsonify({'message': 'Usuário deletado com sucesso'}), 200
    except LookupError as e:
        return jsonify({'error': str(e)}), 404


@user_bp.route('/users/<int:user_id>/tasks', methods=['GET'])
def get_user_tasks(user_id):
    try:
        return jsonify(UserController.get_user_tasks(user_id)), 200
    except LookupError as e:
        return jsonify({'error': str(e)}), 404


@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    try:
        result = UserController.login(
            email=data.get('email', ''),
            password=data.get('password', ''),
        )
        return jsonify(result), 200
    except PermissionError as e:
        status = 403 if 'inativo' in str(e) else 401
        return jsonify({'error': str(e)}), status
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
