from models.pedido import PedidoModel
from controllers.constants import (
    LIMITE_DESCONTO_ALTO, LIMITE_DESCONTO_MEDIO, LIMITE_DESCONTO_BAIXO,
    TAXA_DESCONTO_ALTO, TAXA_DESCONTO_MEDIO, TAXA_DESCONTO_BAIXO
)


class RelatorioController:

    @staticmethod
    def vendas() -> dict:
        dados = PedidoModel.relatorio()
        faturamento = dados["faturamento"]
        desconto = RelatorioController._calcular_desconto(faturamento)
        total_pedidos = dados["total_pedidos"]
        return {
            "total_pedidos": total_pedidos,
            "faturamento_bruto": faturamento,
            "desconto_aplicavel": round(desconto, 2),
            "faturamento_liquido": round(faturamento - desconto, 2),
            "pedidos_pendentes": dados["pedidos_pendentes"],
            "pedidos_aprovados": dados["pedidos_aprovados"],
            "pedidos_cancelados": dados["pedidos_cancelados"],
            "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0
        }

    @staticmethod
    def _calcular_desconto(faturamento: float) -> float:
        if faturamento > LIMITE_DESCONTO_ALTO:
            return faturamento * TAXA_DESCONTO_ALTO
        if faturamento > LIMITE_DESCONTO_MEDIO:
            return faturamento * TAXA_DESCONTO_MEDIO
        if faturamento > LIMITE_DESCONTO_BAIXO:
            return faturamento * TAXA_DESCONTO_BAIXO
        return 0.0
