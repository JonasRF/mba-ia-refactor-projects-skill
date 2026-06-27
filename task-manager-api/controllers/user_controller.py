from database import db
from models.user import User
from models.task import Task
from controllers.exceptions import ConflictError
from sqlalchemy.orm import joinedload
import re

VALID_ROLES = frozenset(['user', 'admin', 'manager'])
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$')
MIN_PASSWORD_LEN = 4


class UserController:

    @staticmethod
    def get_all() -> list[dict]:
        users = User.query.options(joinedload(User.tasks)).all()
        return [{**user.to_dict(), 'task_count': len(user.tasks)} for user in users]

    @staticmethod
    def get_by_id(user_id: int) -> dict:
        user = db.session.get(User, user_id)
        if not user:
            raise LookupError('Usuário não encontrado')
        data = user.to_dict()
        data['tasks'] = [task.to_dict() for task in Task.query.filter_by(user_id=user_id).all()]
        return data

    @staticmethod
    def create(name: str, email: str, password: str, role: str = 'user') -> dict:
        if not name:
            raise ValueError('Nome é obrigatório')
        if not email or not EMAIL_REGEX.match(email):
            raise ValueError('Email inválido')
        if not password or len(password) < MIN_PASSWORD_LEN:
            raise ValueError('Senha deve ter no mínimo 4 caracteres')
        if role not in VALID_ROLES:
            raise ValueError('Role inválido')
        if User.query.filter_by(email=email).first():
            raise ConflictError('Email já cadastrado')

        user = User(name=name, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user.to_dict()

    @staticmethod
    def update(user_id: int, data: dict) -> dict:
        user = db.session.get(User, user_id)
        if not user:
            raise LookupError('Usuário não encontrado')

        if 'name' in data:
            user.name = data['name']

        if 'email' in data:
            if not EMAIL_REGEX.match(data['email']):
                raise ValueError('Email inválido')
            existing = User.query.filter_by(email=data['email']).first()
            if existing and existing.id != user_id:
                raise ConflictError('Email já cadastrado')
            user.email = data['email']

        if 'password' in data:
            if len(data['password']) < MIN_PASSWORD_LEN:
                raise ValueError('Senha muito curta')
            user.set_password(data['password'])

        if 'role' in data:
            if data['role'] not in VALID_ROLES:
                raise ValueError('Role inválido')
            user.role = data['role']

        if 'active' in data:
            user.active = data['active']

        db.session.commit()
        return user.to_dict()

    @staticmethod
    def delete(user_id: int) -> None:
        user = db.session.get(User, user_id)
        if not user:
            raise LookupError('Usuário não encontrado')
        Task.query.filter_by(user_id=user_id).delete()
        db.session.delete(user)
        db.session.commit()

    @staticmethod
    def get_user_tasks(user_id: int) -> list[dict]:
        if not db.session.get(User, user_id):
            raise LookupError('Usuário não encontrado')
        return [task.to_dict() for task in Task.query.filter_by(user_id=user_id).all()]

    @staticmethod
    def login(email: str, password: str) -> dict:
        if not email or not password:
            raise ValueError('Email e senha são obrigatórios')
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            raise PermissionError('Credenciais inválidas')
        if not user.active:
            raise PermissionError('Usuário inativo')
        return {
            'message': 'Login realizado com sucesso',
            'user': user.to_dict(),
            'token': f'placeholder-{user.id}',
        }
