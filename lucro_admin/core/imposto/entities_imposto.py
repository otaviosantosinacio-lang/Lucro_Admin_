from dataclasses import dataclass


@dataclass
class ProdutoComImposto:
    """
    ProdutoComImposto

    Attributes:
        id_bling: Id único da venda gerado pelo Bling
        situacao_pedido: Situação do pedido dentro do Bling
        sku: SKU do produto
        quantidade: Quantidade do item vendido
        valor: Valor de venda do produto
        icms: Valor pago de ICMS
        pis: Valor pago de PIS
        cofins: Valor pago de COFINS
        difal: Valor pago de DIFAL
        fcp: Valor pago de FCP
        total: Valor total de imposto pago na venda do produto
    """

    id_bling: int
    situacao_pedido: str
    sku: str
    quantidade: int
    preco_custo: float
    valor: float
    icms: float
    pis: float
    cofins: float
    difal: float
    fcp: float
    total: float


@dataclass
class ImpostosDaVenda:
    """ImpostosDaVenda

    Attributes:
        id_bling: Id único gerado pelo Bling
        icms: Valor pago de ICMS
        pis: Valor pago de PIS
        cofins: Valor pago de COFINS
        difal: Valor pago de DIFAL
        total: Valor total de imposto pago na venda
    """

    id_bling: int
    icms: float
    pis: float
    cofins: float
    difal: float
    fcp: float
    total: float
    custo: float

    @classmethod
    def soma_impostos(cls, produtos_imposto, id_bling) -> 'ImpostosDaVenda':
        """Soma de impostos dos produtos para gerar total de impostos para a venda

        :param cls:
        :param produtos_imposto: Lista com produtos individualizados com impostos
        :param id_bling: Id único gerado pelo Bling
        :return: Retorno formatado para impostos da venda
        :rtype: ImpostosDaVenda
        """
        return cls(
            id_bling=id_bling,
            icms=sum(p.icms for p in produtos_imposto),
            pis=sum(p.pis for p in produtos_imposto),
            cofins=sum(p.cofins for p in produtos_imposto),
            difal=sum(p.difal for p in produtos_imposto),
            fcp=sum(p.fcp for p in produtos_imposto),
            total=sum(p.total for p in produtos_imposto),
            custo=sum(p.preco_custo for p in produtos_imposto),
        )


@dataclass
class RetornoImpostos:
    """
    RetornoImpostos

    Attributes:
        produto_imposto: É uma lista com produtos individualizado com impostos pagos.
        venda_imposto: São os impostos totais da venda.

    """

    produto_imposto: list[ProdutoComImposto]
    venda_imposto: ImpostosDaVenda


@dataclass
class ItemPedido:
    """
    ItemPedido66666666

    Attributes:
        codigo: SKU do produto
        quantidade: Quantidade vendida
        valor: Valor de venda
    """

    codigo: str
    quantidade: int
    valor: float


@dataclass
class ErrorParse:
    """
    ErrorParse

    Attributes:
        tag: Tag do XML que não foi encontrada
        error: Tipo de erro.

    """

    tag: str
    error: str
