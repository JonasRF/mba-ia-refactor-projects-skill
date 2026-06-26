from database.connection import get_db


class ProdutoModel:

    @staticmethod
    def get_todos() -> list:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM produtos WHERE ativo = 1")
        return [ProdutoModel._row_to_dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_por_id(produto_id: int):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
        row = cursor.fetchone()
        return ProdutoModel._row_to_dict(row) if row else None

    @staticmethod
    def criar(nome: str, descricao: str, preco: float, estoque: int, categoria: str) -> int:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
            (nome, descricao, preco, estoque, categoria)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def atualizar(produto_id: int, nome: str, descricao: str, preco: float, estoque: int, categoria: str) -> None:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
            (nome, descricao, preco, estoque, categoria, produto_id)
        )
        db.commit()

    @staticmethod
    def deletar(produto_id: int) -> None:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
        db.commit()

    @staticmethod
    def decrementar_estoque(produto_id: int, quantidade: int) -> None:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
            (quantidade, produto_id)
        )

    @staticmethod
    def buscar(termo: str = "", categoria: str = None, preco_min: float = None, preco_max: float = None) -> list:
        db = get_db()
        cursor = db.cursor()
        sql = "SELECT * FROM produtos WHERE ativo = 1"
        params = []
        if termo:
            sql += " AND (nome LIKE ? OR descricao LIKE ?)"
            params += [f"%{termo}%", f"%{termo}%"]
        if categoria:
            sql += " AND categoria = ?"
            params.append(categoria)
        if preco_min is not None:
            sql += " AND preco >= ?"
            params.append(preco_min)
        if preco_max is not None:
            sql += " AND preco <= ?"
            params.append(preco_max)
        cursor.execute(sql, params)
        return [ProdutoModel._row_to_dict(row) for row in cursor.fetchall()]

    @staticmethod
    def count() -> int:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM produtos")
        return cursor.fetchone()[0]

    @staticmethod
    def _row_to_dict(row) -> dict:
        return {
            "id": row["id"],
            "nome": row["nome"],
            "descricao": row["descricao"],
            "preco": row["preco"],
            "estoque": row["estoque"],
            "categoria": row["categoria"],
            "ativo": bool(row["ativo"]),
            "criado_em": row["criado_em"]
        }
