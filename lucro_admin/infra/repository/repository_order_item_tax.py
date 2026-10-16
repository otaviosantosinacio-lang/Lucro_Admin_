import logging
from dataclasses import asdict

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from lucro_admin.infra.db_error_handle import handler_db_error

logger = logging.getLogger('lucroadmin.infra.repository.order_item_tax')


class OrderItemTax:

    def __init__(self, session: AsyncSession):
        self.session = session

        # ==========================
        #           INSERT
        # ==========================

    @handler_db_error
    async def insert_tax_items(self, items_tax):

        query = text(
            '''
                INSERT INTO order_item_tax(
                    order_item_id,
                    tax_type,
                    tax_value,
                    calculation_source,
                    created_user_id,
                    updated_user_id
                )
                VALUES(
                    :order_item_id,
                    :tax_type,
                    :tax_value,
                    :calculation_source,
                    1,
                    1
                )
            ON CONFLICT ON CONSTRAINT uq_item_pedido_imposto_tipo DO NOTHING;
            '''
        )

        values = [asdict(item_tax)for item_tax in items_tax]

        await self.session.execute(query, values)
        logger.info('Lucro Admin Repository |'
        ' New %s order item tax added.',
        len(values)
        )

    @handler_db_error
    async def select_xml_url(
            self,
            order_id
    ):

        query = text(
            '''
                SELECT
                    ti.order_id,
                    ti.url_xml
                FROM tax_invoice ti
                WHERE ti.order_id = :order_id
            '''
        )

        values = {
            'order_id': order_id
        }

        result = await self.session.execute(query, values)
        data = result.fetchone()
        return data

        # ==========================
        #           SELECT
        # ==========================

    @handler_db_error
    async def select_order_item(self, order_id):
        query = text(
            '''
                SELECT
                    oi.order_item_id,
                    oi.order_id,
                    p.sku,
                    fp.fulfillment_sku
                FROM order_item oi
                INNER JOIN orders o
                    ON oi.order_id = o.order_id
                INNER JOIN products p
                    ON oi.product_id = p.product_id
                LEFT JOIN fulfillment_product fp
                    ON p.product_id = fp.product_id
                    AND o.marketplace_id = fp.marketplace_id
                WHERE oi.order_id = :order_id
            '''
        )

        values = {
            'order_id': order_id
        }

        result = await self.session.execute(query, values)
        data = result.fetchall()
        return data
