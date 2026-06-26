from database.connection import get_db


class PedidoModel:

    @staticmethod
    def get_por_usuario(usuario_id: int) -> list:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT
                p.id          AS pedido_id,
                p.usuario_id,
                p.status,
                p.total,
                p.criado_em,
                ip.produto_id,
                ip.quantidade,
                ip.preco_unitario,
                pr.nome       AS produto_nome
            FROM pedidos p
            LEFT JOIN itens_pedido ip ON ip.pedido_id = p.id
            LEFT JOIN produtos      pr ON pr.id = ip.produto_id
            WHERE p.usuario_id = ?
            ORDER BY p.id, ip.id
        """, (usuario_id,))
        return PedidoModel._agrupar_pedidos(cursor.fetchall())

    @staticmethod
    def get_todos() -> list:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT
                p.id          AS pedido_id,
                p.usuario_id,
                p.status,
                p.total,
                p.criado_em,
                ip.produto_id,
                ip.quantidade,
                ip.preco_unitario,
                pr.nome       AS produto_nome
            FROM pedidos p
            LEFT JOIN itens_pedido ip ON ip.pedido_id = p.id
            LEFT JOIN produtos      pr ON pr.id = ip.produto_id
            ORDER BY p.id, ip.id
        """)
        return PedidoModel._agrupar_pedidos(cursor.fetchall())

    @staticmethod
    def inserir(usuario_id: int, total: float) -> int:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
            (usuario_id, total)
        )
        return cursor.lastrowid

    @staticmethod
    def inserir_item(pedido_id: int, produto_id: int, quantidade: int, preco_unitario: float) -> None:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
            (pedido_id, produto_id, quantidade, preco_unitario)
        )

    @staticmethod
    def atualizar_status(pedido_id: int, novo_status: str) -> None:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "UPDATE pedidos SET status = ? WHERE id = ?",
            (novo_status, pedido_id)
        )
        db.commit()

    @staticmethod
    def commit() -> None:
        get_db().commit()

    @staticmethod
    def relatorio() -> dict:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM pedidos")
        total_pedidos = cursor.fetchone()[0]
        cursor.execute("SELECT COALESCE(SUM(total), 0) FROM pedidos")
        faturamento = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'pendente'")
        pendentes = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'aprovado'")
        aprovados = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'cancelado'")
        cancelados = cursor.fetchone()[0]
        return {
            "total_pedidos": total_pedidos,
            "faturamento": round(faturamento, 2),
            "pedidos_pendentes": pendentes,
            "pedidos_aprovados": aprovados,
            "pedidos_cancelados": cancelados
        }

    @staticmethod
    def count() -> int:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM pedidos")
        return cursor.fetchone()[0]

    @staticmethod
    def _agrupar_pedidos(rows) -> list:
        pedidos = {}
        for row in rows:
            pedido_id = row["pedido_id"]
            if pedido_id not in pedidos:
                pedidos[pedido_id] = {
                    "id": pedido_id,
                    "usuario_id": row["usuario_id"],
                    "status": row["status"],
                    "total": row["total"],
                    "criado_em": row["criado_em"],
                    "itens": []
                }
            if row["produto_id"]:
                pedidos[pedido_id]["itens"].append({
                    "produto_id": row["produto_id"],
                    "produto_nome": row["produto_nome"],
                    "quantidade": row["quantidade"],
                    "preco_unitario": row["preco_unitario"]
                })
        return list(pedidos.values())
