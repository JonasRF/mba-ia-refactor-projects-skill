import bcrypt
from database.connection import get_db


class UsuarioModel:

    @staticmethod
    def get_todos() -> list:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, nome, email, tipo, criado_em FROM usuarios")
        return [UsuarioModel._row_to_dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_por_id(usuario_id: int):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, nome, email, tipo, criado_em FROM usuarios WHERE id = ?", (usuario_id,))
        row = cursor.fetchone()
        return UsuarioModel._row_to_dict(row) if row else None

    @staticmethod
    def criar(nome: str, email: str, senha_plain: str, tipo: str = "cliente") -> int:
        db = get_db()
        cursor = db.cursor()
        senha_hash = bcrypt.hashpw(senha_plain.encode(), bcrypt.gensalt()).decode()
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
            (nome, email, senha_hash, tipo)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def autenticar(email: str, senha_plain: str):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        row = cursor.fetchone()
        if row and bcrypt.checkpw(senha_plain.encode(), row["senha"].encode()):
            return {
                "id": row["id"],
                "nome": row["nome"],
                "email": row["email"],
                "tipo": row["tipo"]
            }
        return None

    @staticmethod
    def count() -> int:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        return cursor.fetchone()[0]

    @staticmethod
    def _row_to_dict(row) -> dict:
        return {
            "id": row["id"],
            "nome": row["nome"],
            "email": row["email"],
            "tipo": row["tipo"],
            "criado_em": row["criado_em"]
        }
