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

    result = await session.scalar(
        select(Marketplace).where(Marketplace.marketplace_id == 1)
    )

    assert result.marketplace_name == 'Lucro Admin Shop'


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
    session.add_all([user, marketplace, order_situation, order, product])

    await session.flush()

    order_item = OrderItem(
        order_id=1,
        situation_id=1,
        product_id=1,
        quantity=1,
        cost_price=Decimal('59.99'),
        unit_selling_price=Decimal('149.99'),
        item_shipping=Decimal('25.56'),
        item_commission=Decimal('14.99'),
        created_user_id=1,
        updated_user_id=1,
    )

    session.add(order_item)
    await session.commit()

    result = await session.scalar(
        select(OrderItem).where(OrderItem.situation_id == 1)
    )

    assert result is not None
    assert result.order_id == 1


@pytest.mark.asyncio
async def test_create_order_item_tax(session: AsyncSession):
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

    await session.flush()

    order_item = OrderItem(
        order_id=1,
        situation_id=1,
        product_id=1,
        quantity=1,
        cost_price=Decimal('59.99'),
        unit_selling_price=Decimal('149.99'),
        item_shipping=Decimal('25.56'),
        item_commission=Decimal('14.99'),
        created_user_id=1,
        updated_user_id=1,
    )

    session.add_all(
        [
            user,
            marketplace,
            order_situation,
            order,
            product,
            order_item
            ]
    )

    await session.flush()

    order_item_tax = OrderItemTax(
        order_item_id=1,
        tax_type='ICMS',
        tax_value=Decimal('10.00'),
        calculation_source='Calculo Manual',
        created_user_id=1,
        updated_user_id=1,
    )

    session.add(order_item_tax)
    await session.commit()

    result = await session.scalar(
        select(OrderItemTax).where(OrderItemTax.order_item_id == 1)
    )

    assert result is not None
    assert result.order_item_tax_id == 1


@pytest.mark.asyncio
async def test_create_tax_invoice(session: AsyncSession):
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

    await session.flush()

    order_item = OrderItem(
        order_id=1,
        situation_id=1,
        product_id=1,
        quantity=1,
        cost_price=Decimal('59.99'),
        unit_selling_price=Decimal('149.99'),
        item_shipping=Decimal('25.56'),
        item_commission=Decimal('14.99'),
        created_user_id=1,
        updated_user_id=1,
    )

    order_item_tax = OrderItemTax(
        order_item_id=1,
        tax_type='ICMS',
        tax_value=Decimal('10.00'),
        calculation_source='Calculo Manual',
        created_user_id=1,
        updated_user_id=1,
    )
    session.add_all(
        [
            user,
            marketplace,
            order_situation,
            order,
            product,
            order_item,
            order_item_tax
            ]
    )
    await session.flush()

    tax_invoice = TaxInvoice(
        order_id=1,
        url_xml='www.lucroadmin.com/xml/?3456381578910456375930195749382746519305',
        serie=6,
        issue_date=date(2026, 6, 3),
        bling_tax_invoice_id=6748420,
        created_user_id=1,
        updated_user_id=1,
        tax_invoice_value=Decimal('56.51'),
        key_access=None,
    )

    session.add(tax_invoice)
    await session.commit()

    result = await session.scalar(
        select(TaxInvoice).where(TaxInvoice.tax_invoice_id == 1)
    )

    assert result is not None
    assert result.tax_invoice_id == 1
