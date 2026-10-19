from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Produto:
    sku: str
    nome: str
    preco_custo: float


@dataclass
class Product:
    external_product_id: int
    sku: str
    product_description: str
    supplier: str
    cost_price: Decimal
    origin: int
    ncm: str
    cest: str
