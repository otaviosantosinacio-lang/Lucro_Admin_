from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from lucro_admin.infra.models.base import BaseModel, table_registry_base

if TYPE_CHECKING:
    from lucro_admin.infra.models.integration import Integrations
    from lucro_admin.infra.models.user import User


@table_registry_base.mapped_as_dataclass
class Marketplace(BaseModel):
    __tablename__ = 'marketplaces'

    marketplace_id: Mapped[int] = mapped_column(
        primary_key=True, nullable=False, init=False
    )

    marketplace_external_id: Mapped[int] = mapped_column(
        nullable=False, unique=True
    )

    external_type: Mapped[str] = mapped_column(
        nullable=True
    )

    marketplace_name: Mapped[str] = mapped_column(nullable=False)

    slug: Mapped[str] = mapped_column(nullable=True)

    status: Mapped[str] = mapped_column(
        Boolean,
        init=False,
        nullable=False,
        default=True,
        server_default='true',
    )

    integration_erp: Mapped[int] = mapped_column(
        ForeignKey('integrations.integration_id'),
        nullable=False
    )

    integration_marketplace: Mapped[int] = mapped_column(
        ForeignKey('integrations.integration_id'),
        nullable=True
    )
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

    intregation_erp_id: Mapped['Integrations'] = mapped_column(
        foreign_keys=[integration_erp],
        init=False
    )

    intregation_marketplace_id: Mapped['Integrations'] = mapped_column(
        foreign_keys=[integration_marketplace],
        init=False
    )

    created_user: Mapped['User'] = relationship(
        foreign_keys=[created_user_id], init=False
    )

    updated_user: Mapped['User'] = relationship(
        foreign_keys=[updated_user_id], init=False
    )
