from datetime import datetime
from sqlalchemy.orm import registry, Mapped, mapped_column


registro_tabela = registry()

@registro_tabela.mapped_as_dataclass
class Usuario:
    __tablename__ = 'usuarios'

    id_usuario: Mapped[int] = mapped_column(init =False, primary_key=True)
    nome_usuario: Mapped[str] = mapped_column(unique=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    senha_hash: Mapped[str]
    status_usuario: Mapped[str]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime] 