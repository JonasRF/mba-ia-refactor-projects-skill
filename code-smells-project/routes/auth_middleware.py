import os
from functools import wraps

import jwt
from flask import request, jsonify

from controllers.constants import JWT_ALGORITHM


def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return jsonify({"erro": "Token ausente"}), 401
        token = header.removeprefix("Bearer ")
        try:
            payload = jwt.decode(token, os.environ["SECRET_KEY"], algorithms=[JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            return jsonify({"erro": "Token expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"erro": "Token inválido"}), 401
        request.usuario_id = payload["sub"]
        request.usuario_role = payload["role"]
        return f(*args, **kwargs)
    return wrapper


def require_admin(f):
    @wraps(f)
    @require_auth
    def wrapper(*args, **kwargs):
        if request.usuario_role != "admin":
            return jsonify({"erro": "Acesso restrito a administradores"}), 403
        return f(*args, **kwargs)
    return wrapper
