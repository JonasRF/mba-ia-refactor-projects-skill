from flask import Blueprint, request, jsonify
from controllers.task_controller import TaskController
from datetime import datetime

task_bp = Blueprint('tasks', __name__)


def _parse_due_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d')
    except ValueError:
        raise ValueError('Formato de data inválido. Use YYYY-MM-DD')


def _parse_int(value, field_name: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValueError(f"'{field_name}' deve ser um número inteiro válido")


@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    try:
        tasks = TaskController.get_all()
        return jsonify(tasks), 200
    except Exception:
        return jsonify({'error': 'Erro interno'}), 500


@task_bp.route('/tasks/search', methods=['GET'])
def search_tasks():
    try:
        filters = {}
        if request.args.get('q'):
            filters['q'] = request.args.get('q')
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('priority'):
            filters['priority'] = _parse_int(request.args.get('priority'), 'priority')
        if request.args.get('user_id'):
            filters['user_id'] = _parse_int(request.args.get('user_id'), 'user_id')
        return jsonify(TaskController.get_all(filters=filters)), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@task_bp.route('/tasks/stats', methods=['GET'])
def task_stats():
    return jsonify(TaskController.get_stats()), 200


@task_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    try:
        return jsonify(TaskController.get_by_id(task_id)), 200
    except LookupError as e:
        return jsonify({'error': str(e)}), 404


@task_bp.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    try:
        due_date = _parse_due_date(data.get('due_date'))
        task = TaskController.create(
            title=data.get('title', ''),
            description=data.get('description', ''),
            status=data.get('status', 'pending'),
            priority=data.get('priority', 3),
            user_id=data.get('user_id'),
            category_id=data.get('category_id'),
            due_date=due_date,
            tags=data.get('tags'),
        )
        return jsonify(task), 201
    except LookupError as e:
        return jsonify({'error': str(e)}), 404
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@task_bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    try:
        if 'due_date' in data:
            data['due_date'] = _parse_due_date(data['due_date'])
        return jsonify(TaskController.update(task_id, data)), 200
    except LookupError as e:
        return jsonify({'error': str(e)}), 404
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@task_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        TaskController.delete(task_id)
        return jsonify({'message': 'Task deletada com sucesso'}), 200
    except LookupError as e:
        return jsonify({'error': str(e)}), 404
