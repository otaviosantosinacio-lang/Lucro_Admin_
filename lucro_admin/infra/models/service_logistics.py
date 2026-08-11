from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from lucro_admin.infra.models.base import BaseModel, table_registry_base

if TYPE_CHECKING:
    from lucro_admin.infra.models.user import User


@table_registry_base.mapped_as_dataclass
class ServiceLogistics(BaseModel):
    __tablename__ = 'services_logistics'

    service_id: Mapped[int] = mapped_column(init=False, primary_key=True)

    external_service_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=False
    )

    service_name: Mapped[str] = mapped_column(
        unique=True
    )

    logistics_name: Mapped[str] = mapped_column(
        nullable=True
    )

    status: Mapped[bool]

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

    created_user: Mapped['User'] = relationship(
        foreign_keys=[created_user_id], init=False
    )

    updated_user: Mapped['User'] = relationship(
        foreign_keys=[updated_user_id], init=False
    )
