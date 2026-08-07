from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from lucro_admin.infra.models.base import BaseModel, table_registry_base

if TYPE_CHECKING:
    from lucro_admin.infra.models.order import Order
    from lucro_admin.infra.models.pipeline_stage import PipelineStage
    from lucro_admin.infra.models.pipeline_status import PipelineStatus

@table_registry_base.mapped_as_dataclass
class PipelineExecution(BaseModel):
    __tablename__ = 'pipeline_execution'

    pipeline_id: Mapped[int] = mapped_column(init=False, primary_key=True)

    order_id: Mapped[int] = mapped_column(
        ForeignKey('orders.order_id'),
        nullable=False
    )

    stage_id: Mapped[int] = mapped_column(
        ForeignKey('pipeline_stage.stage_id'), nullable=False
        )

    status_id: Mapped[int] = mapped_column(
        ForeignKey('pipeline_status.status_id'),
        nullable=False
    )

    attempts: Mapped[str] = mapped_column(nullable=False)

    description: Mapped[str] = mapped_column(nullable=False)

    order: Mapped[Order] = relationship(
        foreign_keys=[order_id],
        init=False
    )

    status: Mapped[PipelineStatus] = relationship(
        foreign_keys=[status_id],
        init=False
    )

    stage: Mapped[PipelineStage] = relationship(
        foreign_keys=[stage_id],
        init=False
    )
