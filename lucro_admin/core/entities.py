from dataclasses import dataclass
from datetime import datetime


@dataclass
class PageOrders:
    id: int | None
    date_page: datetime
    situation_id: int
    integration_id: int
