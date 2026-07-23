from datetime import datetime

from sqlalchemy import Boolean, func
from sqlalchemy.orm import Mapped, mapped_column

from lucro_admin.infra.models.base import BaseModel, table_registry_base


@table_registry_base.mapped_as_dataclass
class BlingOrderSituation(BaseModel):
    __tablename__ = 'bling_orders_situation'

    situation_id: Mapped[int] = mapped_column(init=False, primary_key=True)

    situation_bling_id: Mapped[int] = mapped_column(
        unique=True,
        nullable=False
    )

    situation_name: Mapped[str] = mapped_column(nullable=False)

    situation_color: Mapped[str] = mapped_column(nullable=False)

    status: Mapped[str] = mapped_column(
        Boolean,
        init=False,
        nullable=False,
        default=True,
        server_default='true',
    )

    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )
