from datetime import datetime

from sqlalchemy import func, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from lucro_admin.infra.models.base import registro_tabela

@registro_tabela.mapped_as_dataclass
class Situacao_Pedido_Bling:
    __tablename__ = 'situacoes_pedidos_bling'

    id_situacao: Mapped[int] = mapped_column(
        init=False,
        primary_key=True
    )
    
    id_situacao_bling: Mapped[int] = mapped_column(
        unique=True,
        nullable=False
    )
    
    nome_situacao: Mapped[str] = mapped_column(
        nullable=False
    )
    
    cor_situacao: Mapped[str] = mapped_column(
        nullable=False
    )
    
    status: Mapped[str] = mapped_column(
        Boolean,
        init=False,
        nullable=False,
        default=True,
        server_default='true',
    )
    
    created_at: Mapped[datetime] = mapped_column(
        init=False,
        server_default=func.now()
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        init=False,
        server_default=func.now(),
        onupdate=func.now()
    )
