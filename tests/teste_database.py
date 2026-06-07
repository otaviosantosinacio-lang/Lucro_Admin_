from sqlalchemy import select

from lucro_admin.models import Situacao_Pedido_Bling, Usuario


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


def teste_criar_situacao_pedido_bling(session):
    situacao_pedido = Situacao_Pedido_Bling(9, 'Atendido', 'Azul')

    session.add(situacao_pedido)
    session.commit()

    resultado = session.scalar(
        select(Situacao_Pedido_Bling).where(
            Situacao_Pedido_Bling.id_situacao_bling == 9
        )
    )

    assert resultado.nome_situacao == 'Atendido'
