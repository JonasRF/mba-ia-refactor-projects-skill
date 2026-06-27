from database import db
from models.category import Category
from models.task import Task


class CategoryController:

    @staticmethod
    def get_all() -> list[dict]:
        categories = Category.query.all()
        return [
            {**cat.to_dict(), 'task_count': Task.query.filter_by(category_id=cat.id).count()}
            for cat in categories
        ]

    @staticmethod
    def create(name: str, description: str = '', color: str = '#000000') -> dict:
        if not name:
            raise ValueError('Nome é obrigatório')
        category = Category(name=name, description=description, color=color)
        db.session.add(category)
        db.session.commit()
        return category.to_dict()

    @staticmethod
    def update(cat_id: int, data: dict) -> dict:
        cat = db.session.get(Category, cat_id)
        if not cat:
            raise LookupError('Categoria não encontrada')
        if 'name' in data:
            cat.name = data['name']
        if 'description' in data:
            cat.description = data['description']
        if 'color' in data:
            cat.color = data['color']
        db.session.commit()
        return cat.to_dict()

    @staticmethod
    def delete(cat_id: int) -> None:
        cat = db.session.get(Category, cat_id)
        if not cat:
            raise LookupError('Categoria não encontrada')
        db.session.delete(cat)
        db.session.commit()
