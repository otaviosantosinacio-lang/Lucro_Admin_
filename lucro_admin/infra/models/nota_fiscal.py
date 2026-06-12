from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from lucro_admin.infra.models.base import registro_tabela

if TYPE_CHECKING:

@registro_tabela.mapped_as_dataclass
class Nota_Fiscal:
    
    __tablename__ = 'notas_fiscais'

    id_nf: Mapped[int]= mapped_column(
        init=False,
        primary_key=True
    )

    id_nf_bling: Mapped[int]= mapped_column(
        nullable=True
    )

    id_pedido: Mapped[int]= mapped_column(
        ForeignKey('pedidos.id_pedido'),
        nullable=False
    )

    url_xml: Mapped[str]= mapped_column(
        nullable=True
    )

    serie: Mapped[int]= mapped_column(
        nullable=True
    )

    chave_acesso: Mapped[str]= mapped_column(
        unique=True,
        nullable=True
    )

    data_emissao: Mapped[date]