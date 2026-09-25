import logging
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Literal

logger = logging.getLogger('lucroadmin.core.entities')


@dataclass
class BlingSituation:
    """
    BlingSituation -> Standardized formatting for order situations within Bling

    Attributes:
        cod_sit: Situation code
        :type cod_sit: int
        name_sit: Name of the Situation (Ex: Atendido)
        :type name_sit: str
    """

    situation_bling_id: int
    situation_name: str
    situation_color: str | None = None


@dataclass
class BlingSituationDB:
    situation_id: int
    situation_bling_id: int
    situation_name: str
    situation_color: str | None = None


@dataclass
class PageResult:
    """
        PageResult -> Standardizing the return of requests for Bling endpoints.

        Attributes:
            status: status of the request return.
            :type status: Literal [ok, rated_limit, error]
            data: Data from the request.
            :type data: Any | None = None
            error: In case there's an error, we put it in this attribute to handle it.
            :type error: Any = None
    """  # noqa: E501

    status: Literal['ok', 'rated_limit', 'error']
    data: Any | None = None
    error: Any = None


@dataclass
class ErrorHTTP:
    """
    ErrorHTTP -> HTTP error standardization, so we can handle the fallback
    after active executions

    Attributes:
        status:We use by default the same status from the PageResult Class (ok, rated_limit, error).
        :type status: Literal ['rated_limit', 'error']
        error: It's the same error already set up in the paginaResultado Class, that is, it's the response body of the request.
        :type error: Any
        method: It's the method used, meaning the executed def that encountered the error.
        :type method: str
        class_name: The class to which the method belongs
        :type class: str
        module: The file where the method is located.
        :type module: str
        endpoint: The API Endpoint where the request was made
        :type endpoint: str
        data: The exact date of sending this request
        :type data: datetime
    """  # noqa: E501

    status: Literal['rated_limit', 'error']
    error: Any
    method: str
    class_name: str
    module: str
    endpoint: str
    data: datetime


@dataclass
class GetPagesResult:
    """
    GetPagesResult -> Result of the get_id_por_pag method

    Attributes:
        sales_id: List with all unique Bling IDs per sale
        :type sales_id: list[int]
        endpointerror: List with specifications of the endpoint where we got an error response. Type ErrorHTTP
        :type endpointerror: list[ErrorHTTP]
        situation: Name of the situation the obtained orders are in (Ex: Cancelado)
        :type situation: str
    """  # noqa: E501

    sales_id: list[int]
    endpointerro: list[ErrorHTTP]
    situation: str

@dataclass
class OrderByPage:
    external_id: int
    origin_id: int
    situation_id: int
    marketplace_id: int
    marketplace_order_id: str
    order_date: date


@dataclass
class OrderDetail:
    """
    GetDetailsResult -> Result of the get_id_details method

    Attributes:
        order_id: Unique id order
        :type order_id: int
        external_invoice_id: External tax invoice id
        :type endpointerror: int
        value_order: Total order value
        :type value_order: float
    """  # noqa: E501

    order_id: int
    external_invoice_id: int
    value_order: float
    uf_dest: str
    transport: str


@dataclass
class ItemList:
    order_id: int
    situation_id: int
    items: list[Any]


@dataclass
class OrderItemInsert:
    order_id: int
    situation_id: int
    product_id: int
    quantity: int
    cost_price: float
    unit_selling_price: float


@dataclass
class ItemComissionShip:
    order_item_id: int
    item_shipping: float
    item_commission: float


@dataclass
class IdsPedidoML:
    comissao: float
    pay_id: int
    pack_id: int
    geral: Any
    status: Literal['ok', 'rated_limit', 'error']


@dataclass
class SaleCosts:
    costs: list[ItemComissionShip]
