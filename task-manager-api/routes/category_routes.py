from flask import Blueprint, request, jsonify
from controllers.category_controller import CategoryController

category_bp = Blueprint('categories', __name__)


@category_bp.route('/categories', methods=['GET'])
def get_categories():
    return jsonify(CategoryController.get_all()), 200


@category_bp.route('/categories/create', methods=['POST'])
def create_category():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    try:
        category = CategoryController.create(
            name=data.get('name', ''),
            description=data.get('description', ''),
            color=data.get('color', '#000000'),
        )
        return jsonify(category), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@category_bp.route('/categories/<int:cat_id>', methods=['PUT'])
def update_category(cat_id):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    try:
        return jsonify(CategoryController.update(cat_id, data)), 200
    except LookupError as e:
        return jsonify({'error': str(e)}), 404
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@category_bp.route('/categories/<int:cat_id>', methods=['DELETE'])
def delete_category(cat_id):
    try:
        CategoryController.delete(cat_id)
        return jsonify({'message': 'Categoria deletada'}), 200
    except LookupError as e:
        return jsonify({'error': str(e)}), 404
