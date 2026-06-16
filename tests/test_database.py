from sqlalchemy import select

from lucro_admin.infra.models.usuario import Usuario
from lucro_admin.infra.models.situacao_pedidos_bling import SituacaoPedidoBling

def teste_criar_usuario(session):

    usuario = Usuario(
        nome_usuario='otavio123',
        email='otavio@lucro_admin.com',
        senha_hash='otavio@123',
        
    )

    session.add(usuario)
    session.commit()

    resultado = session.scalar(
        select(Usuario).where(Usuario.email == 'otavio@lucro_admin.com')
    )
    assert resultado.nome_usuario == 'otavio123'



