from __future__ import annotations
from datetime import datetime

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship

if TYPE_CHECKING:
    from lucro_admin.infra.models.usuario import Usuario

registro_tabela = registry()

@registro_tabela.mapped_as_dataclass
class Marketplace:
    id_marketplace: Mapped[int] = mapped_column(primary_key=True, nullable=False, init=False)
    nome_marketplace: Mapped[str] = mapped_column(nullable=False, unique=True)
    status: Mapped[str] = mapped_column(
        Boolean,
    )
    created_at: Mapped[datetime]= mapped_column(init=False, server_default=func.now())
    created_user_id: Mapped[int]= mapped_column(ForeignKey("usuario.id_usuario"))
