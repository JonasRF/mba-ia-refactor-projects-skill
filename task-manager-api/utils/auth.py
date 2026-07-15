from functools import wraps
from flask import request, jsonify, current_app
import jwt


def require_auth(f):
    """Decorator de rota que exige um JWT válido no header Authorization: Bearer <token>.

    Em caso de sucesso, disponibiliza o payload decodificado em `request.user`
    (contém `sub` = user_id e `role`).
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        header = request.headers.get('Authorization', '')
        if not header.startswith('Bearer '):
            return jsonify({'error': 'Token ausente'}), 401

        token = header.removeprefix('Bearer ').strip()
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token inválido'}), 401

        request.user = payload
        return f(*args, **kwargs)
    return wrapper
