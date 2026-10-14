from dataclasses import dataclass
from datetime import date


@dataclass
class PageOrders:
    id: int | None
    date_page: date
    situation_id: int
    integration_id: int
