from dataclasses import dataclass
from datetime import date


@dataclass
class PageOrders:
    id: int | None
    date_page: date
    page: int
    more_orders: bool
    situation_id: int
    integration_id: int
