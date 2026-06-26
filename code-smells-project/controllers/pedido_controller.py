from models.produto import ProdutoModel
from models.pedido import PedidoModel
from services.notification_service import NotificationService
from controllers.constants import STATUS_PEDIDO


class PedidoController:

    def __init__(self, notifier: NotificationService = None):
        self.notifier = notifier or NotificationService()

    def criar(self, usuario_id: int, itens: list) -> dict:
        if not usuario_id:
            raise ValueError("usuario_id é obrigatório")
        if not itens:
            raise ValueError("Pedido deve ter pelo menos 1 item")

        total = 0.0
        produtos_cache = {}
        for item in itens:
            produto_id = item["produto_id"]
            produto = ProdutoModel.get_por_id(produto_id)
            if not produto:
                raise LookupError(f"Produto {produto_id} não encontrado")
            if produto["estoque"] < item["quantidade"]:
                raise ValueError(f"Estoque insuficiente para {produto['nome']}")
            total += produto["preco"] * item["quantidade"]
            produtos_cache[produto_id] = produto

        pedido_id = PedidoModel.inserir(usuario_id, total)

        for item in itens:
            produto = produtos_cache[item["produto_id"]]
            PedidoModel.inserir_item(pedido_id, item["produto_id"], item["quantidade"], produto["preco"])
            ProdutoModel.decrementar_estoque(item["produto_id"], item["quantidade"])

        PedidoModel.commit()
        self.notifier.pedido_criado(pedido_id, usuario_id)
        return {"pedido_id": pedido_id, "total": total}

    def listar_por_usuario(self, usuario_id: int) -> list:
        return PedidoModel.get_por_usuario(usuario_id)

    def listar_todos(self) -> list:
        return PedidoModel.get_todos()

    def atualizar_status(self, pedido_id: int, novo_status: str) -> None:
        if novo_status not in STATUS_PEDIDO:
            raise ValueError(f"Status inválido. Válidos: {sorted(STATUS_PEDIDO)}")
        PedidoModel.atualizar_status(pedido_id, novo_status)
        self.notifier.pedido_status_atualizado(pedido_id, novo_status)
