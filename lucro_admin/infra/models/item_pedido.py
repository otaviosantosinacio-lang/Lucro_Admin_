from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, func
from lucro_admin.infra.models.base import registro_tabela

@registro_tabela.mapped_as_dataclass
class ItemPedido:

    id_item_pedido: Mapped[int]= mapped_column(
        primary_key=True,
        init=False
    )

    id_pedido: Mapped[int]= mapped_column(
        ForeignKey('pedidos.id_pedido'),
        nullable=False
    )