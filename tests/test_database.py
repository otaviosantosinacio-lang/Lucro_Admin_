from sqlalchemy import select
from decimal import Decimal

from lucro_admin.infra.models.usuario import Usuario
from lucro_admin.infra.models.situacao_pedidos_bling import SituacaoPedidoBling
from lucro_admin.infra.models.produto import Produto
from lucro_admin.infra.models.marketplace import Marketplace


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
    
    situacao_pedido = SituacaoPedidoBling(
        9, 'Atendido', 'Azul'
    )

    session.add(situacao_pedido)
    session.commit()

    resultado = session.scalar(
        select(SituacaoPedidoBling).where(
            SituacaoPedidoBling.id_situacao_bling == 9
        )
    )

    assert resultado.nome_situacao == 'Atendido'
    
def teste_criar_produto(session):
    
    usuario= Usuario(
        nome_usuario='otavio123',
        email='otavio@lucro_admin.com',
        senha_hash='otavio@123'
    )
    
    produto= Produto(
        id_produto_bling= 13579,
        sku= 'LADM0001',
        descricao_produto= 'gerenciador de lucro',
        fornecedor= 'Lucro Admin',
        preco_custo= Decimal('29.99'),
        created_user_id = 1,
        updated_user_id= 1
    )
    
    session.add(usuario)
    session.flush()
    
    session.add(produto)
    session.commit()
    
    resultado= session.scalar(
        select(Produto).where(
            Produto.id_produto_bling == 13579
        )
    )
    
    assert resultado.sku == 'LADM0001'
    
def teste_criando_marketplace(session):
    
    usuario= Usuario(
        nome_usuario='otavio123',
        email='otavio@lucro_admin.com',
        senha_hash='otavio@123'
    )
        
    marketplace= Marketplace(
        nome_marketplace= 'Lucro Admin Shop',
        created_user_id= 1,
        updated_user_id= 1
    )
        
    session.add(usuario)
    session.flush()
        
    session.add(marketplace)
    session.commit()
        
    resultado= session.scalar(
        select(Marketplace).where(
            Marketplace.id_marketplace == 1
        )
    )
        
    assert resultado.nome_marketplace == 'Lucro Admin Shop'
    

    
    
    
