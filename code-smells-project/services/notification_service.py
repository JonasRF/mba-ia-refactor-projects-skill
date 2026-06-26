class NotificationService:

    def pedido_criado(self, pedido_id: int, usuario_id: int) -> None:
        print(f"[EMAIL] Pedido {pedido_id} criado para usuário {usuario_id}")
        print(f"[SMS]   Pedido {pedido_id} recebido com sucesso!")
        print(f"[PUSH]  Novo pedido {pedido_id} no sistema")

    def pedido_status_atualizado(self, pedido_id: int, novo_status: str) -> None:
        if novo_status == "aprovado":
            print(f"[NOTIF] Pedido {pedido_id} aprovado — preparar envio")
        elif novo_status == "cancelado":
            print(f"[NOTIF] Pedido {pedido_id} cancelado — devolver estoque")
