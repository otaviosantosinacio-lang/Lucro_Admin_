from __future__ import annotations
from decimal import Decimal

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, func
from lucro_admin.infra.models.base import registro_tabela
from datetime import datetime

@registro_tabela.mapped_as_dataclass
class Produto:
    id_produto: Mapped[int]= mapped_column(
        init=False,
        primary_key=True
    )

    id_produto_bling: Mapped[int]= mapped_column(
        unique=True,
        nullable=False
    )

    sku: Mapped[str]= mapped_column(
        unique=True,
        nullable=True
    )

    descricao_produto: Mapped[str]

    fornecedor: Mapped[str]

    preco_custo: Mapped[Decimal]
    
    created_at: Mapped[datetime]= mapped_column(
        init=False,
        server_default=func.now()
    )

    