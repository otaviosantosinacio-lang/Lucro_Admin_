from sqlalchemy.orm import Mapped, mapped_column

from lucro_admin.infra.models.base import BaseModel, table_registry_base


@table_registry_base.mapped_as_dataclass
class Integrations(BaseModel):
    __tablename__ = 'integrations'

    integration_id: Mapped[int] = mapped_column(
        init=False,
        primary_key=True,
        nullable=False
    )

    name: Mapped[str] = mapped_column(
        nullable=False,
        unique=True
    )

    type: Mapped[str] = mapped_column(
        nullable=False
    )
