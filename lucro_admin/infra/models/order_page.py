from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from lucro_admin.infra.models.base import BaseModel, table_registry_base

if TYPE_CHECKING:
    from lucro_admin.infra.models.bling_order_situation import (
        BlingOrderSituation,
    )
    from lucro_admin.infra.models.integration import Integrations


@table_registry_base.mapped_as_dataclass
class OrderPage(BaseModel):
    __tablename__ = 'order_page'

    id: Mapped[int] = mapped_column(
        init=False,
        primary_key=True
    )

    date_page: Mapped[date] = mapped_column(nullable=False)

    page: Mapped[int] = mapped_column(nullable=False)

    more_orders: Mapped[bool] = mapped_column(nullable=False)

    situation_id: Mapped[int] = mapped_column(
        nullable=False
    )

    integration_id: Mapped[int] = mapped_column(
        ForeignKey('integrations.integration_id'),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        init=False,
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )

    page_integration: Mapped['Integrations'] = relationship(
        foreign_keys=[integration_id],
        init=False
    )
