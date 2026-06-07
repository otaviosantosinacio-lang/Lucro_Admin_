import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal

logger = logging.getLogger('lucroadmin.core.entities')


@dataclass
class SituacaoBling:
    """
    SituacaoBling -> Formatação padronizada para situações do pedido dentro do bling.

    Attributes:
        cod_sit: Código da situação
        :type cod_sit: int
        nome_sit: Nome da Situação (Ex: Atendido)
        :type nome_sit: str
    """

    cod_sit: int
    nome_sit: str


@dataclass
class ResultadoPagina:
    """
    ResultadoPagina -> Padronizando retorno dos requets para endpoints Bling.

    Attributes:
        status: status do retorno da requisição. (Ex: ok = 200, rated_limit = 429)
        :type status: Literal [ok, rated_limit, error]
        data: Dados da requisição.
        :type data: Any | None = None
        error: Caso haja erro inserimos nesse atributo para trata-lo.
        :type error: Any = None
    """

    status: Literal['ok', 'rated_limit', 'error']
    data: Any | None = None
    error: Any = None


@dataclass
class ErrorHTTP:
    """
    ErrorHTTP -> Padronização de erros http, para tratarmos o fallback após execuções ativas

    Attributes:
        status: Utilizamos por padrão o mesmo status da Class ResultadoPagina (ok, rated_limit, error). Para ter mais assertividade recomendo setar já o status obtido no resultado pagina (Ex: status = response.error['status'])
        :type status: Literal ['rated_limit', 'error']
        error: É o mesmo error já configurado na Class RasultadoPagina, ou seja, é o body de retorno da requisição.
        :type error: Any
        metodo: É o metodo utilizado, ou seja, a def executada que recebeu o erro.
        :type metodo: str
        classe: A class ao qual pertence o método
        :type classe: str
        local: Arquivo onde está localizado o método.
        :type local: str
        endpoint: EndPoint da API em que foi realizada o request
        :type endpoint: str
        data: Data exata do envio deste request
        :type data: datetime
    """

    status: Literal['rated_limit', 'error']
    error: Any
    metodo: str
    classe: str
    local: str
    endpoint: str
    data: datetime


@dataclass
class ResultadoGetPaginas:
    """
    ResultadoGetPaginas -> Resultado do método get_id_por_pag

    Attributes:
        vendas_id: Lista com todos Id bling único por venda
        :type vendas_id: list[int]
        endpointerror: Lista com especificações da endpoint em que tivemos retorno de erro. Type ErrorHTTP
        :type endpointerror: list[ErrorHTTP]
        situacao: Nome da situação em que os pedidos obtidos estão (Ex: Cancelados)
        :type situacao: str
    """

    vendas_id: list[int]
    endpointerro: list[ErrorHTTP]
    situacao: str


@dataclass
class ResultadoGetDetalhes:
    """
    ResultadoGetDetalhes -> Resultado do método get_id_detalhes

    Attributes:
        pedidos: Lista com todos pedidos consultados. Type DadosPedidos
        :type pedidos: list[DadosPedidos]
        endpointerror: Lista com especificações da endpoint em que tivemos retorno de erro. Type ErrorHTTP
        :type endpointerror: list[ErrorHTTP]
        situacao: Nome da situação em que os pedidos obtidos estão (Ex: Cancelados)
        :type situacao: str
    """

    pedidos: list[Any]
    endpointerror: list[ErrorHTTP]
    situacao: str


@dataclass
class DadosPedidos:
    """
    DadosPedidos -> Formatação e organização dos dados do pedido

    Attributes:
        id_bling: Id único da venda, esse id é gerado pelo bling
        :type id_bling: int
        num_bling: Número único da venda gerado pelo Bling
        :type num_bling: int
        id_mkt: Número da venda gerado pelo Marketplace
        :type id_mkt: int
        data: Data da venda
        :type data: datetime
        nome_loja: Nome da loja onde foi realizada a venda
        :type nome_loja: str
        nf_id: Id único da NF gerado pelo Bling
        :type nd_id: int
        valor_pedido: Valor total da venda
        :type valor_pedido: float
        itens: Dados de todos itens da venda
        :type itens: list
        uf_dest: UF destino da vend
        :type uf_dest: str
    """

    id_bling: int
    num_bling: int
    id_mkt: int
    data: datetime
    nome_loja: str
    nf_id: int
    valor_pedido: float
    itens: list
    uf_dest: str
    servico_trans: str | Any


@dataclass
class Dados_Pedido_imposto:
    id_bling: int
    num_bling: int
    situacao: str
    id_mkt: int
    data: datetime
    nome_loja: str
    nf_id: int
    valor_pedido: float
    servico_trans: str | Any
    icms: float
    pis: float
    cofins: float
    difal: float
    fcp: float
    total: float
    custo_produto: float


@dataclass
class PedidoCompleto:
    id_bling: int
    num_bling: int
    situacao: str
    id_mkt: int
    data: datetime
    nome_loja: str
    nf_id: int
    valor_pedido: float
    icms: float
    pis: float
    cofins: float
    difal: float
    fcp: float
    total_imposto: float
    custo_produto: float
    comissao: float
    frete: float
    lucro: float


@dataclass
class PedidoseImpostos:
    pedidos: list[Any]
    impostos_produto: list[Any]


@dataclass
class ComissaoFrete:
    id_bling: int
    comissao: float
    frete: float


@dataclass
class IdsPedidoML:
    comissao: float
    pay_id: int
    pack_id: int
    geral: Any


@dataclass
class ProdutoCompleto:
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
    total_imposto: float
    frete: float
    comissao: float


@dataclass
class PedidoseProdutosCompletos:
    pedidos: list[Any]
    produtos: list[Any]
