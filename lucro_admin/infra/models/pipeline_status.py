from sqlalchemy.orm import Mapped, mapped_column

from lucro_admin.infra.models.base import BaseModel, table_registry_base


@table_registry_base.mapped_as_dataclass
class PipelineStatus(BaseModel):
    __tablename__ = 'pipeline_status'

    status_id: Mapped[int] = mapped_column(init=False, primary_key=True)

    status_name: Mapped[str] = mapped_column(nullable=False)

    description: Mapped[str] = mapped_column(nullable=False)
