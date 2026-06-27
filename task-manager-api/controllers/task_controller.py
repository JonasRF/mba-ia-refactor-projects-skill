from database import db
from models.task import Task
from models.user import User
from models.category import Category
from sqlalchemy.orm import joinedload
from datetime import datetime

VALID_STATUSES = frozenset(['pending', 'in_progress', 'done', 'cancelled'])
MIN_TITLE_LEN = 3
MAX_TITLE_LEN = 200
MIN_PRIORITY = 1
MAX_PRIORITY = 5


class TaskController:

    @staticmethod
    def get_all(filters=None) -> list[dict]:
        query = Task.query.options(joinedload(Task.user), joinedload(Task.category))
        if filters:
            if filters.get('q'):
                term = filters['q']
                query = query.filter(
                    db.or_(
                        Task.title.like(f'%{term}%'),
                        Task.description.like(f'%{term}%'),
                    )
                )
            if filters.get('status'):
                query = query.filter(Task.status == filters['status'])
            if filters.get('priority') is not None:
                query = query.filter(Task.priority == filters['priority'])
            if filters.get('user_id') is not None:
                query = query.filter(Task.user_id == filters['user_id'])
        return [task.to_dict() for task in query.all()]

    @staticmethod
    def get_by_id(task_id: int) -> dict:
        task = db.session.get(Task, task_id)
        if not task:
            raise LookupError('Task não encontrada')
        return task.to_dict()

    @staticmethod
    def create(title: str, description: str = '', status: str = 'pending',
               priority: int = 3, user_id=None, category_id=None,
               due_date=None, tags=None) -> dict:
        if not title or len(title.strip()) < MIN_TITLE_LEN:
            raise ValueError('Título deve ter no mínimo 3 caracteres')
        if len(title) > MAX_TITLE_LEN:
            raise ValueError('Título muito longo (máx. 200 caracteres)')
        if status not in VALID_STATUSES:
            raise ValueError(f'Status inválido. Valores aceitos: {sorted(VALID_STATUSES)}')
        if not (MIN_PRIORITY <= priority <= MAX_PRIORITY):
            raise ValueError('Prioridade deve ser entre 1 e 5')
        if user_id and not db.session.get(User, user_id):
            raise LookupError('Usuário não encontrado')
        if category_id and not db.session.get(Category, category_id):
            raise LookupError('Categoria não encontrada')

        task = Task(
            title=title.strip(),
            description=description,
            status=status,
            priority=priority,
            user_id=user_id,
            category_id=category_id,
            due_date=due_date,
        )
        if tags:
            task.tags = ','.join(tags) if isinstance(tags, list) else tags

        db.session.add(task)
        db.session.commit()
        db.session.refresh(task)
        return task.to_dict()

    @staticmethod
    def update(task_id: int, data: dict) -> dict:
        task = db.session.get(Task, task_id)
        if not task:
            raise LookupError('Task não encontrada')

        if 'title' in data:
            title = data['title']
            if len(title) < MIN_TITLE_LEN:
                raise ValueError('Título muito curto')
            if len(title) > MAX_TITLE_LEN:
                raise ValueError('Título muito longo')
            task.title = title

        if 'description' in data:
            task.description = data['description']

        if 'status' in data:
            if data['status'] not in VALID_STATUSES:
                raise ValueError('Status inválido')
            task.status = data['status']

        if 'priority' in data:
            if not (MIN_PRIORITY <= data['priority'] <= MAX_PRIORITY):
                raise ValueError('Prioridade deve ser entre 1 e 5')
            task.priority = data['priority']

        if 'user_id' in data:
            if data['user_id'] and not db.session.get(User, data['user_id']):
                raise LookupError('Usuário não encontrado')
            task.user_id = data['user_id']

        if 'category_id' in data:
            if data['category_id'] and not db.session.get(Category, data['category_id']):
                raise LookupError('Categoria não encontrada')
            task.category_id = data['category_id']

        if 'due_date' in data:
            task.due_date = data['due_date']

        if 'tags' in data:
            tags = data['tags']
            task.tags = ','.join(tags) if isinstance(tags, list) else tags

        task.updated_at = datetime.utcnow()
        db.session.commit()
        db.session.refresh(task)
        return task.to_dict()

    @staticmethod
    def delete(task_id: int) -> None:
        task = db.session.get(Task, task_id)
        if not task:
            raise LookupError('Task não encontrada')
        db.session.delete(task)
        db.session.commit()

    @staticmethod
    def get_stats() -> dict:
        total = Task.query.count()
        all_tasks = Task.query.all()
        overdue_count = sum(1 for t in all_tasks if t.is_overdue())
        done_count = Task.query.filter_by(status='done').count()
        return {
            'total': total,
            'pending': Task.query.filter_by(status='pending').count(),
            'in_progress': Task.query.filter_by(status='in_progress').count(),
            'done': done_count,
            'cancelled': Task.query.filter_by(status='cancelled').count(),
            'overdue': overdue_count,
            'completion_rate': round((done_count / total) * 100, 2) if total > 0 else 0,
        }
