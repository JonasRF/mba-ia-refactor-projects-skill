from database import db
from models.task import Task
from models.user import User
from models.category import Category
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta


class ReportController:

    @staticmethod
    def summary() -> dict:
        total_tasks = Task.query.count()
        done_count = Task.query.filter_by(status='done').count()
        seven_days_ago = datetime.utcnow() - timedelta(days=7)

        all_tasks = Task.query.all()
        overdue_list = [
            {
                'id': task.id,
                'title': task.title,
                'due_date': str(task.due_date),
                'days_overdue': (datetime.utcnow() - task.due_date).days,
            }
            for task in all_tasks if task.is_overdue()
        ]

        users = User.query.options(joinedload(User.tasks)).all()
        user_productivity = []
        for user in users:
            total = len(user.tasks)
            completed = sum(1 for task in user.tasks if task.status == 'done')
            user_productivity.append({
                'user_id': user.id,
                'user_name': user.name,
                'total_tasks': total,
                'completed_tasks': completed,
                'completion_rate': round((completed / total) * 100, 2) if total > 0 else 0,
            })

        return {
            'generated_at': str(datetime.utcnow()),
            'overview': {
                'total_tasks': total_tasks,
                'total_users': User.query.count(),
                'total_categories': Category.query.count(),
            },
            'tasks_by_status': {
                'pending': Task.query.filter_by(status='pending').count(),
                'in_progress': Task.query.filter_by(status='in_progress').count(),
                'done': done_count,
                'cancelled': Task.query.filter_by(status='cancelled').count(),
            },
            'tasks_by_priority': {
                'critical': Task.query.filter_by(priority=1).count(),
                'high': Task.query.filter_by(priority=2).count(),
                'medium': Task.query.filter_by(priority=3).count(),
                'low': Task.query.filter_by(priority=4).count(),
                'minimal': Task.query.filter_by(priority=5).count(),
            },
            'overdue': {
                'count': len(overdue_list),
                'tasks': overdue_list,
            },
            'recent_activity': {
                'tasks_created_last_7_days': Task.query.filter(
                    Task.created_at >= seven_days_ago
                ).count(),
                'tasks_completed_last_7_days': Task.query.filter(
                    Task.status == 'done',
                    Task.updated_at >= seven_days_ago,
                ).count(),
            },
            'user_productivity': user_productivity,
        }

    @staticmethod
    def user_report(user_id: int) -> dict:
        user = db.session.get(User, user_id)
        if not user:
            raise LookupError('Usuário não encontrado')

        tasks = Task.query.filter_by(user_id=user_id).all()
        total = len(tasks)
        done = sum(1 for task in tasks if task.status == 'done')
        pending = sum(1 for task in tasks if task.status == 'pending')
        in_progress = sum(1 for task in tasks if task.status == 'in_progress')
        cancelled = sum(1 for task in tasks if task.status == 'cancelled')
        overdue = sum(1 for task in tasks if task.is_overdue())
        high_priority = sum(1 for task in tasks if task.priority <= 2)

        return {
            'user': {'id': user.id, 'name': user.name, 'email': user.email},
            'statistics': {
                'total_tasks': total,
                'done': done,
                'pending': pending,
                'in_progress': in_progress,
                'cancelled': cancelled,
                'overdue': overdue,
                'high_priority': high_priority,
                'completion_rate': round((done / total) * 100, 2) if total > 0 else 0,
            },
        }
