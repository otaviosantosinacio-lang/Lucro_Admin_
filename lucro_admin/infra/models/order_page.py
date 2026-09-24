from datetime import date, datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from lucro_admin.infra.models.base import BaseModel, table_registry_base


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

    created_at: Mapped[datetime] = mapped_column(
        init=False,
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )
