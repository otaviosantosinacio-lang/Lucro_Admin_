from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from lucro_admin.infra.models.item_pedido import ItemPedido
from lucro_admin.infra.models.item_pedido_imposto import ItemPedidoImposto
from lucro_admin.infra.models.marketplace import Marketplace
from lucro_admin.infra.models.nota_fiscal import NotaFiscal
from lucro_admin.infra.models.pedido import Pedido
from lucro_admin.infra.models.produto import Produto
from lucro_admin.infra.models.situacao_pedidos_bling import SituacaoPedidoBling
from lucro_admin.infra.models.usuario import Usuario


@pytest.mark.asyncio
async def teste_criar_usuario(session: AsyncSession):

    usuario = Usuario(
        nome_usuario='otavio123',
        email='otavio@lucro_admin.com',
        senha_hash='otavio@123',
    )

    session.add(usuario)
    await session.commit()

    resultado = await session.scalar(
        select(Usuario).where(Usuario.email == 'otavio@lucro_admin.com')
    )

    assert resultado is not None
    assert resultado.nome_usuario == 'otavio123'


@pytest.mark.asyncio
async def teste_criar_situacao_pedido_bling(session: AsyncSession):

    situacao_pedido = SituacaoPedidoBling(9, 'Atendido', 'Azul')

    session.add(situacao_pedido)
    await session.commit()

    resultado = await session.scalar(
        select(SituacaoPedidoBling).where(
            SituacaoPedidoBling.id_situacao_bling == 9
        )
    )

    assert resultado is not None
    assert resultado.nome_situacao == 'Atendido'


@pytest.mark.asyncio
async def teste_criar_produto(session: AsyncSession):

    usuario = Usuario(
        nome_usuario='otavio123',
        email='otavio@lucro_admin.com',
        senha_hash='otavio@123',
    )

    produto = Produto(
        id_produto_bling=13579,
        sku='LADM0001',
        descricao_produto='gerenciador de lucro',
        fornecedor='Lucro Admin',
        preco_custo=Decimal('29.99'),
        created_user_id=1,
        updated_user_id=1,
    )

    session.add(usuario)
    await session.flush()

    session.add(produto)
    await session.commit()

    resultado = await session.scalar(
        select(Produto).where(Produto.id_produto_bling == 13579)
    )

    assert resultado is not None
    assert resultado.sku == 'LADM0001'


@pytest.mark.asyncio
async def teste_criando_marketplace(session):

    usuario = Usuario(
        nome_usuario='otavio123',
        email='otavio@lucro_admin.com',
        senha_hash='otavio@123',
    )

    marketplace = Marketplace(
        nome_marketplace='Lucro Admin Shop',
        created_user_id=1,
        updated_user_id=1,
    )

    session.add(usuario)
    await session.flush()

    session.add(marketplace)
    await session.commit()

    resultado = await session.scalar(
        select(Marketplace).where(Marketplace.id_marketplace == 1)
    )

    assert resultado.nome_marketplace == 'Lucro Admin Shop'


@pytest.mark.asyncio
async def teste_criando_pedido(session: AsyncSession):

    usuario = Usuario(
        nome_usuario='otavio123',
        email='otavio@lucro_admin.com',
        senha_hash='otavio@123',
    )

    marketplace = Marketplace(
        nome_marketplace='Lucro Admin Shop',
        created_user_id=1,
        updated_user_id=1,
    )

    situacao_pedido = SituacaoPedidoBling(9, 'Atendido', 'Azul')

    session.add_all([usuario, marketplace, situacao_pedido])

    await session.flush()

    pedido = Pedido(
        id_bling=120543543,
        num_bling=12387,
        id_situacao=1,
        id_nf_bling=150789,
        id_marketplace=1,
        id_pedido_marketplace=20000456382042,
        data_venda=date(2026, 5, 25),
        valor_pedido=Decimal('160.00'),
        created_user_id=1,
        updated_user_id=1,
    )

    session.add(pedido)
    await session.commit()

    resultado = await session.scalar(
        select(Pedido).where(Pedido.num_bling == 12387)
    )

    assert resultado is not None
    assert resultado.id_pedido_marketplace == 20000456382042


@pytest.mark.asyncio
async def teste_criando_item_pedido(session: AsyncSession):

    usuario = Usuario(
        nome_usuario='otavio123',
        email='otavio@lucro_admin.com',
        senha_hash='otavio@123',
    )

    produto = Produto(
        id_produto_bling=13579,
        sku='LADM0001',
        descricao_produto='gerenciador de lucro',
        fornecedor='Lucro Admin',
        preco_custo=Decimal('29.99'),
        created_user_id=1,
        updated_user_id=1,
    )

    marketplace = Marketplace(
        nome_marketplace='Lucro Admin Shop',
        created_user_id=1,
        updated_user_id=1,
    )

    situacao_pedido = SituacaoPedidoBling(9, 'Atendido', 'Azul')

    pedido = Pedido(
        id_bling=120543543,
        num_bling=12387,
        id_situacao=1,
        id_nf_bling=150789,
        id_marketplace=1,
        id_pedido_marketplace=20000456382042,
        data_venda=date(2026, 5, 25),
        valor_pedido=Decimal('160.00'),
        created_user_id=1,
        updated_user_id=1,
    )

    session.add_all([usuario, marketplace, situacao_pedido, pedido, produto])

    await session.flush()

    item_pedido = ItemPedido(
        id_pedido=1,
        id_situacao=1,
        id_produto=1,
        quantidade=1,
        preco_custo=Decimal('59.99'),
        preco_venda_unitario=Decimal('149.99'),
        frete_item=Decimal('25.56'),
        comissao_item=Decimal('14.99'),
        created_user_id=1,
        updated_user_id=1,
    )

    session.add(item_pedido)
    await session.commit()

    resultado = await session.scalar(
        select(ItemPedido).where(ItemPedido.id_situacao == 1)
    )

    assert resultado is not None
    assert resultado.id_pedido == 1


@pytest.mark.asyncio
async def teste_criando_item_pedido_imposto(session: AsyncSession):
    usuario = Usuario(
        nome_usuario='otavio123',
        email='otavio@lucro_admin.com',
        senha_hash='otavio@123',
    )

    produto = Produto(
        id_produto_bling=13579,
        sku='LADM0001',
        descricao_produto='gerenciador de lucro',
        fornecedor='Lucro Admin',
        preco_custo=Decimal('29.99'),
        created_user_id=1,
        updated_user_id=1,
    )

    marketplace = Marketplace(
        nome_marketplace='Lucro Admin Shop',
        created_user_id=1,
        updated_user_id=1,
    )

    situacao_pedido = SituacaoPedidoBling(9, 'Atendido', 'Azul')

    pedido = Pedido(
        id_bling=120543543,
        num_bling=12387,
        id_situacao=1,
        id_nf_bling=150789,
        id_marketplace=1,
        id_pedido_marketplace=20000456382042,
        data_venda=date(2026, 5, 25),
        valor_pedido=Decimal('160.00'),
        created_user_id=1,
        updated_user_id=1,
    )

    item_pedido = ItemPedido(
        id_pedido=1,
        id_situacao=1,
        id_produto=1,
        quantidade=1,
        preco_custo=Decimal('59.99'),
        preco_venda_unitario=Decimal('149.99'),
        frete_item=Decimal('25.56'),
        comissao_item=Decimal('14.99'),
        created_user_id=1,
        updated_user_id=1,
    )

    session.add_all([
        usuario,
        marketplace,
        situacao_pedido,
        pedido,
        produto,
        item_pedido,
    ])

    await session.flush()

    item_pedido_imposto = ItemPedidoImposto(
        id_item_pedido=1,
        tipo_imposto='ICMS',
        valor_imposto=Decimal('10.00'),
        origem_calculo='Calculo Manual',
        created_user_id=1,
        updated_user_id=1,
    )

    session.add(item_pedido_imposto)
    await session.commit()

    resultado = await session.scalar(
        select(ItemPedidoImposto).where(ItemPedidoImposto.id_item_pedido == 1)
    )

    assert resultado is not None
    assert resultado.id_item_pedido_imposto == 1


@pytest.mark.asyncio
async def test_criando_nota_fiscal(session: AsyncSession):
    usuario = Usuario(
        nome_usuario='otavio123',
        email='otavio@lucro_admin.com',
        senha_hash='otavio@123',
    )

    produto = Produto(
        id_produto_bling=13579,
        sku='LADM0001',
        descricao_produto='gerenciador de lucro',
        fornecedor='Lucro Admin',
        preco_custo=Decimal('29.99'),
        created_user_id=1,
        updated_user_id=1,
    )

    marketplace = Marketplace(
        nome_marketplace='Lucro Admin Shop',
        created_user_id=1,
        updated_user_id=1,
    )

    situacao_pedido = SituacaoPedidoBling(9, 'Atendido', 'Azul')

    pedido = Pedido(
        id_bling=120543543,
        num_bling=12387,
        id_situacao=1,
        id_nf_bling=150789,
        id_marketplace=1,
        id_pedido_marketplace=20000456382042,
        data_venda=date(2026, 5, 25),
        valor_pedido=Decimal('160.00'),
        created_user_id=1,
        updated_user_id=1,
    )

    session.add_all([usuario, produto, marketplace, situacao_pedido, pedido])

    await session.flush()

    nota_fiscal = NotaFiscal(
        id_pedido=1,
        url_xml='www.lucroadmin.com/xml/?3456381578910456375930195749382746519305',
        serie=6,
        data_emissao=date(2026, 6, 3),
        id_nf_bling=6748420,
        created_user_id=1,
        updated_user_id=1,
        valor_nf=Decimal('56.51'),
        chave_acesso=None,
    )

    session.add(nota_fiscal)
    await session.commit()

    resultado = await session.scalar(
        select(NotaFiscal).where(NotaFiscal.id_nf == 1)
    )

    assert resultado is not None
    assert resultado.id_nf == 1
