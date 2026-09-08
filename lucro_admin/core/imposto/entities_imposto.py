from dataclasses import dataclass
from datetime import date


@dataclass
class TaxItem:
    order_item_id: int
    tax_type: str
    tax_value: float
    calculation_source: str


@dataclass
class OrderItem:
    """
    OrderItem

    Attributes:
        code: Product SKU
        quantity: Quantity sold
        value: Sale value
    """

    code: str
    quantity: int
    value: float


@dataclass
class ErrorParse:
    """
    ErrorParse

    Attributes:
        tag: XML tag that was not found
        error: Type of error.

    """

    tag: str
    error: str


@dataclass
class InsertTaxInvoice:
    order_id: int
    url_xml: str
    serie: int
    key_access: str
    issue_date: date
    tax_invoice_value: float
