from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from lucro_admin.infra.models.bling_order_situation import BlingOrderSituation
from lucro_admin.infra.models.marketplace import Marketplace
from lucro_admin.infra.models.order import Order
from lucro_admin.infra.models.order_item import OrderItem
from lucro_admin.infra.models.order_item_tax import OrderItemTax
from lucro_admin.infra.models.product import Product
from lucro_admin.infra.models.tax_invoice import TaxInvoice
from lucro_admin.infra.models.user import User


@pytest.mark.asyncio
async def test_create_user(session: AsyncSession):

    user = User(
        user_name='otavio123',
        email='otavio@lucro_admin.com',
        password='otavio@123',
    )

    session.add(user)
    await session.commit()

    result = await session.scalar(
        select(User).where(User.email == 'otavio@lucro_admin.com')
    )

    assert result is not None
    assert result.user_name == 'otavio123'


@pytest.mark.asyncio
async def test_create_bling_order_situation(session: AsyncSession):

    order_situation = BlingOrderSituation(9, 'Atendido', 'Azul')

    session.add(order_situation)
    await session.commit()

    result = await session.scalar(
        select(BlingOrderSituation).where(
            BlingOrderSituation.situation_bling_id == 9
        )
    )

    assert result is not None
    assert result.situation_name == 'Atendido'


@pytest.mark.asyncio
async def test_create_product(session: AsyncSession):

    user = User(
        user_name='otavio123',
        email='otavio@lucro_admin.com',
        password='otavio@123',
    )

    product = Product(
        product_bling_id=13579,
        sku='LADM0001',
        product_description='gerenciador de lucro',
        supplier='Lucro Admin',
        cost_price=Decimal('29.99'),
        origin=1,
        ncm='123456',
        cest='456789',
        created_user_id=1,
        updated_user_id=1,
    )

    session.add(user)
    await session.flush()

    session.add(product)
    await session.commit()

    result = await session.scalar(
        select(Product).where(Product.product_bling_id == 13579)
    )

    assert result is not None
    assert result.sku == 'LADM0001'


@pytest.mark.asyncio
async def test_create_marketplace(session):

    user = User(
        user_name='otavio123',
        email='otavio@lucro_admin.com',
        password='otavio@123',
    )

    marketplace = Marketplace(
        marketplace_name='Lucro Admin Shop',
        created_user_id=1,
        updated_user_id=1,
    )

    session.add(user)
    await session.flush()

    session.add(marketplace)
    await session.commit()

    resultado = await session.scalar(
        select(Marketplace).where(Marketplace.marketplace_id == 1)
    )

    assert resultado.nome_marketplace == 'Lucro Admin Shop'


@pytest.mark.asyncio
async def teste_criando_pedido(session: AsyncSession):

    user = User(
        user_name='otavio123',
        email='otavio@lucro_admin.com',
        password='otavio@123',
    )

    marketplace = Marketplace(
        marketplace_name='Lucro Admin Shop',
        created_user_id=1,
        updated_user_id=1,
    )

    order_situation = BlingOrderSituation(9, 'Atendido', 'Azul')

    session.add_all([user, marketplace, order_situation])

    await session.flush()

    order = Order(
        bling_id=120543543,
        bling_num=12387,
        situation_id=1,
        tax_invoice_bling_id=150789,
        marketplace_id=1,
        marketplace_order_id=20000456382042,
        order_date=date(2026, 5, 25),
        value_order=Decimal('160.00'),
        created_user_id=1,
        updated_user_id=1,
    )

    session.add(order)
    await session.commit()

    result = await session.scalar(
        select(Order).where(Order.bling_num == 12387)
    )

    assert result is not None
    assert result.marketplace_order_id == 20000456382042


@pytest.mark.asyncio
async def test_creat_order_item(session: AsyncSession):

    user = User(
        user_name='otavio123',
        email='otavio@lucro_admin.com',
        password='otavio@123',
    )

    product = Product(
        product_bling_id=13579,
        sku='LADM0001',
        product_description='gerenciador de lucro',
        supplier='Lucro Admin',
        cost_price=Decimal('29.99'),
        origin=1,
        ncm='123456',
        cest='456789',
        created_user_id=1,
        updated_user_id=1,
    )

    marketplace = Marketplace(
        marketplace_name='Lucro Admin Shop',
        created_user_id=1,
        updated_user_id=1,
    )

    order_situation = BlingOrderSituation(9, 'Atendido', 'Azul')

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
        origem=1,
        ncm='123456',
        cest='456789',
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
        origem=1,
        ncm='123456',
        cest='456789',
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
