from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from lucro_admin.infra.models.base import registro_tabela

if TYPE_CHECKING:
    from lucro_admin.infra.models.usuario import Usuario


@registro_tabela.mapped_as_dataclass
class Produto:
    __tablename__ = 'produtos'

    id_produto: Mapped[int] = mapped_column(init=False, primary_key=True)

    id_produto_bling: Mapped[int] = mapped_column(unique=True, nullable=False)

    sku: Mapped[str] = mapped_column(unique=True, nullable=True)

    descricao_produto: Mapped[str]

    fornecedor: Mapped[str]

    preco_custo: Mapped[Decimal]

    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )

    created_user_id: Mapped[int] = mapped_column(
        ForeignKey('usuarios.id_usuario'), nullable=True
    )

    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )

    updated_user_id: Mapped[int] = mapped_column(
        ForeignKey('usuarios.id_usuario'), nullable=False
    )

    created_user: Mapped['Usuario'] = relationship(
        foreign_keys=[created_user_id], init=False
    )

    updated_user: Mapped['Usuario'] = relationship(
        foreign_keys=[updated_user_id], init=False
    )
