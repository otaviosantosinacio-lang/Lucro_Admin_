from __future__ import annotations
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, func
from lucro_admin.infra.models.base import registro_tabela

@registro_tabela.mapped_as_dataclass
class ItemPedido:

    __tablename__= 'item_pedido'

    id_item_pedido: Mapped[int]= mapped_column(
        primary_key=True,
        init=False
    )

    id_pedido: Mapped[int]= mapped_column(
        ForeignKey('pedidos.id_pedido'),
        nullable=False
    )

    id_situacao: Mapped[int]= mapped_column(
        ForeignKey('situacoes_pedidos_bling.id_situacao'),
        nullable=False
    )

    id_produto: Mapped[int]= mapped_column(
        ForeignKey('produtos.id_produto'),
        nullable=False
    )

    quantidade: Mapped[int]= mapped_column(
        nullable=False
    )

    preco_custo: Mapped[Decimal]= mapped_column(
        nullable=False
    )

    preco_venda_unitario: Mapped[Decimal]= mapped_column(
        nullable=False
    )

    frete_item: Mapped[Decimal]= mapped_column(
        nullable=False
    )

    comissao_item: Mapped[Decimal]= mapped_column(
        nullable=False 
    )

    created_at: Mapped[datetime]= mapped_column(
        init=False,
        server_default=func.now()
    )

    created_user_id: Mapped[int]= mapped_column(
        
    )