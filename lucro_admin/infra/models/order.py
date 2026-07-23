from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from lucro_admin.infra.models.base import BaseModel, table_registry_base

if TYPE_CHECKING:
    from lucro_admin.infra.models.bling_order_situation import (
        BlingOrderSituation,
    )
    from lucro_admin.infra.models.marketplace import Marketplace
    from lucro_admin.infra.models.user import User


@table_registry_base.mapped_as_dataclass
class Order(BaseModel):
    __tablename__ = 'orders'

    order_id: Mapped[int] = mapped_column(init=False, primary_key=True)

    bling_id: Mapped[int] = mapped_column(unique=True)

    bling_num: Mapped[int] = mapped_column(unique=True)

    situation_id: Mapped[int] = mapped_column(
        ForeignKey('bling_orders_situation.id_situacao'), nullable=False
    )

    tax_invoice_bling_id: Mapped[int] = mapped_column(nullable=True)

    marketplace_id: Mapped[int] = mapped_column(
        ForeignKey('marketplaces.id_marketplace'), nullable=True
    )

    marketplace_order_id: Mapped[int] = mapped_column(nullable=False)

    order_date: Mapped[date] = mapped_column(nullable=False)

    value_order: Mapped[Decimal] = mapped_column(nullable=True)

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

    situacao_pedido: Mapped['BlingOrderSituation'] = relationship(
        foreign_keys=[situation_id], init=False
    )

    marketplace_pedido: Mapped['Marketplace'] = relationship(
        foreign_keys=[marketplace_id], init=False
    )

    created_user: Mapped['User'] = relationship(
        foreign_keys=[created_user_id], init=False
    )

    updated_user: Mapped['User'] = relationship(
        foreign_keys=[updated_user_id], init=False
    )
