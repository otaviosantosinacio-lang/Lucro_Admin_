from sqlalchemy import select
from decimal import Decimal
from datetime import date

from lucro_admin.infra.models.usuario import Usuario
from lucro_admin.infra.models.situacao_pedidos_bling import SituacaoPedidoBling
from lucro_admin.infra.models.produto import Produto
from lucro_admin.infra.models.marketplace import Marketplace
from lucro_admin.infra.models.pedido import Pedido
from lucro_admin.infra.models.item_pedido import ItemPedido
from lucro_admin.infra.models.item_pedido_imposto import ItemPedidoImposto

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
    

def teste_criando_pedido(session):
    
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
    
    situacao_pedido = SituacaoPedidoBling(
        9, 'Atendido', 'Azul'
    )

    session.add_all([
        usuario,
        marketplace,
        situacao_pedido
    ])

    session.flush()

    pedido= Pedido(
        id_bling= 120543543,
        num_bling= 12387,
        id_situacao=1,
        id_nf_bling= 150789,
        id_marketplace= 1,
        id_pedido_marketplace= 20000456382042,
        data_venda= date(2026, 5, 25),
        valor_pedido= Decimal('160.00'),
        created_user_id= 1,
        updated_user_id=1
    )

    session.add(pedido)
    session.commit()

    resultado= session.scalar(
        select(Pedido).where(
            Pedido.num_bling == 12387
        )
    )

    assert resultado.id_pedido_marketplace == 20000456382042

def teste_criando_item_pedido(session):

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

    marketplace= Marketplace(
        nome_marketplace= 'Lucro Admin Shop',
        created_user_id= 1,
        updated_user_id= 1
    )
    
    situacao_pedido = SituacaoPedidoBling(
        9, 'Atendido', 'Azul'
    )

    pedido= Pedido(
        id_bling= 120543543,
        num_bling= 12387,
        id_situacao=1,
        id_nf_bling= 150789,
        id_marketplace= 1,
        id_pedido_marketplace= 20000456382042,
        data_venda= date(2026, 5, 25),
        valor_pedido= Decimal('160.00'),
        created_user_id= 1,
        updated_user_id=1
    )

    session.add_all(
        [
            usuario,
            marketplace,
            situacao_pedido,
            pedido,
            produto
        ]
    )

    session.flush()

    item_pedido= ItemPedido(
        id_pedido=1,
        id_situacao=1,
        id_produto= 1,
        quantidade=1,
        preco_custo=Decimal('59.99'),
        preco_venda_unitario=Decimal('149.99'),
        frete_item=Decimal('25.56'),
        comissao_item=Decimal('14.99'),
        created_user_id=1,
        updated_user_id=1
    )    

    session.add(item_pedido)
    session.commit()

    resultado= session.scalar(
        select(ItemPedido).where(
            ItemPedido.id_situacao == 1
        )
    )

    assert resultado.id_pedido == 1

def teste_criando_item_pedido_imposto(session):
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

    marketplace= Marketplace(
        nome_marketplace= 'Lucro Admin Shop',
        created_user_id= 1,
        updated_user_id= 1
    )
    
    situacao_pedido = SituacaoPedidoBling(
        9, 'Atendido', 'Azul'
    )

    pedido= Pedido(
        id_bling= 120543543,
        num_bling= 12387,
        id_situacao=1,
        id_nf_bling= 150789,
        id_marketplace= 1,
        id_pedido_marketplace= 20000456382042,
        data_venda= date(2026, 5, 25),
        valor_pedido= Decimal('160.00'),
        created_user_id= 1,
        updated_user_id=1
    )

    item_pedido= ItemPedido(
        id_pedido=1,
        id_situacao=1,
        id_produto= 1,
        quantidade=1,
        preco_custo=Decimal('59.99'),
        preco_venda_unitario=Decimal('149.99'),
        frete_item=Decimal('25.56'),
        comissao_item=Decimal('14.99'),
        created_user_id=1,
        updated_user_id=1
    )    

    session.add_all(
        [
            usuario,
            marketplace,
            situacao_pedido,
            pedido,
            produto,
            item_pedido
        ]
    )

    session.flush()
    
    item_pedido_imposto= ItemPedidoImposto(
        id_item_pedido=1,
        tipo_imposto='ICMS',
        valor_imposto=Decima('10.00'),
        origem_calculo='Calculo Manual',
        created_user_id=1,
        updated_user_id=1
    )

    session.add(item_pedido_imposto)
    session.commit()

    resultado= session.scalar(
        select(ItemPedidoImposto).where(
            ItemPedidoImposto.id_item_pedido == 1
        )
    )

    assert resultado.id_item_pedido_imposto == 1
    
