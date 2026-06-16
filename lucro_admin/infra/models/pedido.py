from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from lucro_admin.infra.models.base import registro_tabela

if TYPE_CHECKING:
    from lucro_admin.infra.models.situacao_pedidos_bling import (
        SituacaoPedidoBling)
    from lucro_admin.infra.models.marketplace import Marketplace
    from lucro_admin.infra.models.usuario import Usuario



@registro_tabela.mapped_as_dataclass
class Pedido:
    __tablename__ = 'pedidos'

    id_pedido: Mapped[int]= mapped_column(
        init=False, 
        primary_key=True
    )
    
    id_bling: Mapped[int]= mapped_column(
        unique=True
    )
    
    num_bling: Mapped[int]= mapped_column(
        unique=True
    )
    
    id_situacao: Mapped[int]= mapped_column(
        ForeignKey('situacoes_pedidos_bling.id_situacao'),
        nullable=False   
    )
    
    id_nf_bling: Mapped[int]= mapped_column(
        nullable=True
    )
    
    id_marketplace: Mapped[int]= mapped_column(
        ForeignKey('marketplaces.id_marketplace'),
        nullable=False
    )
    
    id_pedido_marketplace: Mapped[int]= mapped_column(
        nullable=True
    )

    data_venda: Mapped[date]= mapped_column(
        nullable=False
    )

    valor_pedido: Mapped[Decimal]= mapped_column(
        nullable=False
    )
    
    created_at: Mapped[datetime]= mapped_column(
        init=False,
        server_default=func.now()
    )

    created_user_id: Mapped[int]= mapped_column(
        ForeignKey('usuarios.id_usuario'),
        nullable= False
    )

    updated_at: Mapped[datetime]= mapped_column(
        init=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    updated_user_id: Mapped[int]= mapped_column(
        ForeignKey('usuarios.id_usuario'),
        nullable=False
    )

    situacao_pedido: Mapped['SituacaoPedidoBling']= relationship(
        foreign_keys=[id_situacao],
        init=False
    )

    marketplace_pedido: Mapped['Marketplace']= relationship(
        foreign_keys=[id_marketplace],
        init=False
    )

    created_user: Mapped['Usuario']= relationship(
        foreign_keys=[created_user_id],
        init=False
    )

    updated_user: Mapped['Usuario']= relationship(
        foreign_keys=[updated_user_id],
        init=False
    )