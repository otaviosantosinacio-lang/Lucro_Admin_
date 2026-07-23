from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from lucro_admin.infra.models.base import BaseModel, table_registry_base

if TYPE_CHECKING:
    from lucro_admin.infra.models.bling_order_situation import (
        BlingOrderSituation,
    )
    from lucro_admin.infra.models.order import Order
    from lucro_admin.infra.models.product import Product
    from lucro_admin.infra.models.user import User


@table_registry_base.mapped_as_dataclass
class OrderItem(BaseModel):
    __tablename__ = 'order_item'

    order_item_id: Mapped[int] = mapped_column(primary_key=True, init=False)

    order_id: Mapped[int] = mapped_column(
        ForeignKey('orders.order_id'), nullable=False
    )

    situation_id: Mapped[int] = mapped_column(
        ForeignKey('bling_orders_situation.situation_id'), nullable=False
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey('product.product_id'), nullable=False
    )

    quantity: Mapped[int] = mapped_column(nullable=False)

    cost_price: Mapped[Decimal] = mapped_column(nullable=False)

    unit_selling_price: Mapped[Decimal] = mapped_column(nullable=False)

    item_shipping: Mapped[Decimal] = mapped_column(nullable=True)

    commission_item: Mapped[Decimal] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )

    created_user_id: Mapped[int] = mapped_column(
        ForeignKey('users.user_id'), nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )

    updated_user_id: Mapped[int] = mapped_column(
        ForeignKey('users.user_id'), nullable=False
    )

    pedido_do_item: Mapped['Order'] = relationship(
        foreign_keys=[order_id], init=False
    )

    situacao_pedido: Mapped['BlingOrderSituation'] = relationship(
        foreign_keys=[situation_id], init=False
    )

    produto_item_pedido: Mapped['Product'] = relationship(
        foreign_keys=[product_id], init=False
    )

    created_user: Mapped['User'] = relationship(
        foreign_keys=[created_user_id], init=False
    )

    update_user: Mapped['User'] = relationship(
        foreign_keys=[updated_user_id], init=False
    )
