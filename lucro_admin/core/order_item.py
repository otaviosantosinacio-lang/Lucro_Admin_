from dataclasses import dataclass


@dataclass
class OrderItemPipeline:
    order_item_id: int
    order_id: int
    marketplace_order_id: int
    transport: str
    sku: str
    fulfillment_sku: str
    pipeline_id: int
    stage_id: int
