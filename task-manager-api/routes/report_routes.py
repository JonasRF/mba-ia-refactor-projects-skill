from flask import Blueprint, jsonify
from controllers.report_controller import ReportController

report_bp = Blueprint('reports', __name__)


@report_bp.route('/reports/summary', methods=['GET'])
def summary_report():
    try:
        return jsonify(ReportController.summary()), 200
    except Exception:
        return jsonify({'error': 'Erro interno'}), 500


@report_bp.route('/reports/user/<int:user_id>', methods=['GET'])
def user_report(user_id):
    try:
        return jsonify(ReportController.user_report(user_id)), 200
    except LookupError as e:
        return jsonify({'error': str(e)}), 404
