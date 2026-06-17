from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from lucro_admin.infra.models.base import registro_tabela

if TYPE_CHECKING:
    from lucro_admin.infra.models.pedido import Pedido
    from lucro_admin.infra.models.usuario import Usuario


@registro_tabela.mapped_as_dataclass
class NotaFiscal:
    __tablename__ = 'notas_fiscais'

    id_nf: Mapped[int] = mapped_column(init=False, primary_key=True)

    id_pedido: Mapped[int] = mapped_column(
        ForeignKey('pedidos.id_pedido'), nullable=False, unique=True
    )

    created_user_id: Mapped[int] = mapped_column(
        ForeignKey('usuarios.id_usuario'), nullable=False
    )

    updated_user_id: Mapped[int] = mapped_column(
        ForeignKey('usuarios.id_usuario'), nullable=False
    )

    url_xml: Mapped[str | None] = mapped_column(nullable=True)

    serie: Mapped[int | None] = mapped_column(nullable=True)

    chave_acesso: Mapped[str | None] = mapped_column(
        unique=True, nullable=True
    )

    data_emissao: Mapped[date | None] = mapped_column(nullable=True)

    valor_nf: Mapped[Decimal | None] = mapped_column(nullable=True)

    id_nf_bling: Mapped[int | None] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )

    nota_fiscal_pedido: Mapped['Pedido'] = relationship(
        foreign_keys=[id_pedido], init=False
    )

    created_user: Mapped['Usuario'] = relationship(
        foreign_keys=[created_user_id], init=False
    )

    updated_user: Mapped['Usuario'] = relationship(
        foreign_keys=[updated_user_id], init=False
    )
