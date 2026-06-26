from models.produto import ProdutoModel
from controllers.constants import CATEGORIAS_PRODUTO


class ProdutoController:

    @staticmethod
    def listar() -> list:
        return ProdutoModel.get_todos()

    @staticmethod
    def buscar(produto_id: int) -> dict:
        produto = ProdutoModel.get_por_id(produto_id)
        if not produto:
            raise LookupError("Produto não encontrado")
        return produto

    @staticmethod
    def criar(nome: str, descricao: str, preco: float, estoque: int, categoria: str) -> dict:
        if len(nome) < 2 or len(nome) > 200:
            raise ValueError("Nome deve ter entre 2 e 200 caracteres")
        if preco < 0:
            raise ValueError("Preço não pode ser negativo")
        if estoque < 0:
            raise ValueError("Estoque não pode ser negativo")
        if categoria not in CATEGORIAS_PRODUTO:
            raise ValueError(f"Categoria inválida. Válidas: {sorted(CATEGORIAS_PRODUTO)}")
        produto_id = ProdutoModel.criar(nome, descricao, preco, estoque, categoria)
        return {"id": produto_id}

    @staticmethod
    def atualizar(produto_id: int, nome: str, descricao: str, preco: float, estoque: int, categoria: str) -> None:
        if not ProdutoModel.get_por_id(produto_id):
            raise LookupError("Produto não encontrado")
        if len(nome) < 2 or len(nome) > 200:
            raise ValueError("Nome deve ter entre 2 e 200 caracteres")
        if preco < 0:
            raise ValueError("Preço não pode ser negativo")
        if estoque < 0:
            raise ValueError("Estoque não pode ser negativo")
        if categoria not in CATEGORIAS_PRODUTO:
            raise ValueError(f"Categoria inválida. Válidas: {sorted(CATEGORIAS_PRODUTO)}")
        ProdutoModel.atualizar(produto_id, nome, descricao, preco, estoque, categoria)

    @staticmethod
    def deletar(produto_id: int) -> None:
        if not ProdutoModel.get_por_id(produto_id):
            raise LookupError("Produto não encontrado")
        ProdutoModel.deletar(produto_id)

    @staticmethod
    def buscar_com_filtros(termo: str, categoria, preco_min, preco_max) -> list:
        return ProdutoModel.buscar(termo, categoria, preco_min, preco_max)
