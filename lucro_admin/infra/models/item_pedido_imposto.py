from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from lucro_admin.infra.models.base import BaseModel, registro_tabela

if TYPE_CHECKING:
    from lucro_admin.infra.models.item_pedido import ItemPedido
    from lucro_admin.infra.models.usuario import Usuario


@registro_tabela.mapped_as_dataclass
class ItemPedidoImposto(BaseModel):
    __tablename__ = 'itens_pedido_imposto'

    __table_args__ = (
        UniqueConstraint(
            'id_item_pedido',
            'tipo_imposto',
            name='uq_item_pedido_imposto_tipo',
        ),
    )

    id_item_pedido_imposto: Mapped[int] = mapped_column(
        primary_key=True, init=False
    )

    id_item_pedido: Mapped[int] = mapped_column(
        ForeignKey('item_pedido.id_item_pedido'), nullable=False
    )

    tipo_imposto: Mapped[str] = mapped_column(nullable=False)

    valor_imposto: Mapped[Decimal]

    origem_calculo: Mapped[str]

    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )

    created_user_id: Mapped[int] = mapped_column(
        ForeignKey('usuarios.id_usuario'), nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )

    updated_user_id: Mapped[int] = mapped_column(
        ForeignKey('usuarios.id_usuario')
    )

    item_pedido: Mapped['ItemPedido'] = relationship(
        foreign_keys=[id_item_pedido], init=False
    )

    creted_user: Mapped['Usuario'] = relationship(
        foreign_keys=[created_user_id], init=False
    )

    updated_user: Mapped['Usuario'] = relationship(
        foreign_keys=[updated_user_id], init=False
    )
