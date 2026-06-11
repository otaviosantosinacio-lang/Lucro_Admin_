from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, registry

from lucro_admin.infra.models.situacao_pedidos_bling import Situacao_Pedido_Bling
registro_tabela = registry()

@registro_tabela.mapped_as_dataclass
class Pedido:
    __tablename__ = 'pedidos'

    id_pedido: Mapped[int] = mapped_column(init=False, primary_key=True)
    id_bling: Mapped[int] = mapped_column(unique=True)
    num_bling: Mapped[int] = mapped_column(unique=True)
    id_situacao: Mapped[int] = mapped_column(
        ForeignKey(Situacao_Pedido_Bling.id_situacao),
        nullable=False   
    )