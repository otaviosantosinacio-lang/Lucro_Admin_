from datetime import datetime

from sqlalchemy import Boolean, func
from sqlalchemy.orm import Mapped, mapped_column

from lucro_admin.infra.models.base import registro_tabela


@registro_tabela.mapped_as_dataclass
class Usuario:
    __tablename__ = 'usuarios'

    id_usuario: Mapped[int] = mapped_column(init=False, primary_key=True)

    nome_usuario: Mapped[str] = mapped_column(unique=True, nullable=False)

    email: Mapped[str] = mapped_column(unique=True, nullable=False)

    senha_hash: Mapped[str] = mapped_column(nullable=False)

    status_usuario: Mapped[bool] = mapped_column(
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
