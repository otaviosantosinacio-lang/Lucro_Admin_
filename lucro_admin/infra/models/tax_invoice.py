from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from lucro_admin.infra.models.base import BaseModel, table_registry_base

if TYPE_CHECKING:
    from lucro_admin.infra.models.order import Order
    from lucro_admin.infra.models.user import User


@table_registry_base.mapped_as_dataclass
class TaxInvoice(BaseModel):
    __tablename__ = 'tax_invoice'

    tax_invoice_id: Mapped[int] = mapped_column(init=False, primary_key=True)

    order_id: Mapped[int] = mapped_column(
        ForeignKey('orders.order_id'), nullable=False, unique=True
    )

    created_user_id: Mapped[int] = mapped_column(
        ForeignKey('users.user_id'), nullable=False
    )

    updated_user_id: Mapped[int] = mapped_column(
        ForeignKey('users.user_id'), nullable=False
    )

    url_xml: Mapped[str | None] = mapped_column(nullable=True)

    serie: Mapped[int | None] = mapped_column(nullable=True)

    key_access: Mapped[str | None] = mapped_column(
        unique=True, nullable=True
    )

    issue_date: Mapped[date | None] = mapped_column(nullable=True)

    tax_invoice_value: Mapped[Decimal | None] = mapped_column(nullable=True)

    bling_tax_invoice_id: Mapped[int | None] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )

    tax_invoice_order: Mapped['Order'] = relationship(
        foreign_keys=[order_id], init=False
    )

    created_user: Mapped['User'] = relationship(
        foreign_keys=[created_user_id], init=False
    )

    updated_user: Mapped['User'] = relationship(
        foreign_keys=[updated_user_id], init=False
    )
