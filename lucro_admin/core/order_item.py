from dataclasses import dataclass


@dataclass
class OrderItemDB:
    order_item_id: int
    order_id: int
    marketplace_order_id: int
    transport: str
    sku: str
    fulfillment_sku: str
