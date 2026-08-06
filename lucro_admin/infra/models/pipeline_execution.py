from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column

from lucro_admin.infra.models.base import BaseModel, table_registry_base

if TYPE_CHECKING:
    from lucro_admin.infra.models.pipeline_stage import PipelineStage


@table_registry_base.mapped_as_dataclass
class PipelineStage(BaseModel):
    __tablename__ = 'pipeline_stage'

    pipeline_id: Mapped[int] = mapped_column(init=False, primary_key=True)

    stage_id: Mapped[int] = mapped_column(
        Foreign_Key=('pipeline_stage.stage_id'), nullable=False
        )
    attempts: Mapped[str] = mapped_column(nullable=False)

    description: Mapped[str] = mapped_column(nullable=False)
