from datetime import datetime

from sqlalchemy import func, Boolean
from sqlalchemy.orm import Mapped, mapped_column, registry


registro_tabela = registry()

@registro_tabela.mapped_as_dataclass
class Marketplace:
    id_marketplace: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    nome_marketplace: Mapped[str] = mapped_column(nullable=False, unique=True)
    status: Mapped[str] = mapped_column(
        Boolean,
    )
