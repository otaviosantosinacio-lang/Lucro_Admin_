from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from lucro_admin.infra.models.base import BaseModel, table_registry_base

if TYPE_CHECKING:
    from lucro_admin.infra.models.order_item import OrderItem
    from lucro_admin.infra.models.user import User


@table_registry_base.mapped_as_dataclass
class OrderItemTax(BaseModel):
    __tablename__ = 'order_item_tax'

    __table_args__ = (
        UniqueConstraint(
            'id_item_pedido',
            'tax_type',
            name='uq_item_pedido_imposto_tipo',
        ),
    )

    order_item_tax_id: Mapped[int] = mapped_column(
        primary_key=True, init=False
    )

    order_item_id: Mapped[int] = mapped_column(
        ForeignKey('order_item.order_item_id'), nullable=False
    )

    tax_type: Mapped[str] = mapped_column(nullable=False)

    tax_value: Mapped[Decimal]

    calculation_source: Mapped[str]

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
        ForeignKey('users.user_id')
    )

    item_pedido: Mapped['OrderItem'] = relationship(
        foreign_keys=[order_item_id], init=False
    )

    creted_user: Mapped['User'] = relationship(
        foreign_keys=[created_user_id], init=False
    )

    updated_user: Mapped['User'] = relationship(
        foreign_keys=[updated_user_id], init=False
    )
