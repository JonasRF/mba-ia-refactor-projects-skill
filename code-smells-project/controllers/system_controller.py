from models.produto import ProdutoModel
from models.usuario import UsuarioModel
from models.pedido import PedidoModel


class SystemController:

    @staticmethod
    def health() -> dict:
        return {
            "status": "ok",
            "database": "connected",
            "counts": {
                "produtos": ProdutoModel.count(),
                "usuarios": UsuarioModel.count(),
                "pedidos": PedidoModel.count()
            },
            "versao": "1.0.0"
        }
