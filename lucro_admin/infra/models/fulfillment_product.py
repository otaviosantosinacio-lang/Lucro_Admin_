from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from lucro_admin.infra.models.base import BaseModel, table_registry_base

if TYPE_CHECKING:
    from lucro_admin.infra.models.product import Product
    from lucro_admin.infra.models.user import User


@table_registry_base.mapped_as_dataclass
class FullProduct(BaseModel):
    __tablename__ = 'fulfillment_product'

    product_full_id: Mapped[int] = mapped_column(
        primary_key=True,
        nullable=False,
        init=False,
        autoincrement=True
    )

    marketplace_id: Mapped[int] = mapped_column(
        ForeignKey('marketplaces.marketplace_id'),
        nullable=False
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey('products.product_id'),
        nullable=False
    )

    fulfillment_sku: Mapped[str] = mapped_column(
        nullable=False,
        unique=True
    )

    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )

    created_user_id: Mapped[int] = mapped_column(
        ForeignKey('users.user_id'),
        nullable=True
    )

    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )

    updated_user_id: Mapped[int] = mapped_column(
        ForeignKey('users.user_id'), nullable=False
    )

    created_user: Mapped['User'] = relationship(
        foreign_keys=[created_user_id], init=False
    )

    updated_user: Mapped['User'] = relationship(
        foreign_keys=[updated_user_id], init=False
    )

    item_product_order: Mapped['Product'] = relationship(
        foreign_keys=[product_id], init=False
    )
