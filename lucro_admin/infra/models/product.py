from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from lucro_admin.infra.models.base import BaseModel, table_registry_base

if TYPE_CHECKING:
    from lucro_admin.infra.models.user import User


@table_registry_base.mapped_as_dataclass
class Product(BaseModel):
    __tablename__ = 'products'

    product_id: Mapped[int] = mapped_column(init=False, primary_key=True)

    product_bling_id: Mapped[int] = mapped_column(unique=True, nullable=False)

    sku: Mapped[str] = mapped_column(unique=True, nullable=True)

    product_description: Mapped[str]

    supplier: Mapped[str]

    cost_price: Mapped[Decimal]

    origin: Mapped[int]

    ncm: Mapped[str]

    cest: Mapped[str]

    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )

    created_user_id: Mapped[int] = mapped_column(
        ForeignKey('users.user_id'), nullable=True
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
