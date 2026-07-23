from datetime import datetime

from sqlalchemy import Boolean, func
from sqlalchemy.orm import Mapped, mapped_column

from lucro_admin.infra.models.base import BaseModel, table_registry_base


@table_registry_base.mapped_as_dataclass
class User(BaseModel):
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(init=False, primary_key=True)

    user_name: Mapped[str] = mapped_column(unique=True, nullable=False)

    email: Mapped[str] = mapped_column(unique=True, nullable=False)

    password: Mapped[str] = mapped_column(nullable=False)

    user_status: Mapped[bool] = mapped_column(
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
