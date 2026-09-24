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
    async def select_searching_xml(
            self,
            offset: int,
            integration_id: int,
            limit=100
    ):

        query = text(
            '''
                SELECT DISTINCT
                    ti.order_id,
                    ti.url_xml
                FROM tax_invoice ti
                INNER JOIN order_item oi
                    ON ti.order_id = oi.order_id
                LEFT JOIN order_item_tax oit
                    ON oi.order_item_id = oit.order_item_id
                INNER JOIN orders o
                    ON ti.order_id = o.order_id
                WHERE oit.order_item_id IS NULL
                    AND o.integration_invoice_id = :integration
                ORDER BY ti.order_id
                OFFSET :offset
                LIMIT :limit
            '''
        )

        values = {
            'integration': integration_id,
            'offset': offset,
            'limit': limit
        }

        result = await self.session.execute(query, values)
        data = result.fetchall()
        return data

        # ==========================
        #           SELECT
        # ==========================

    @handler_db_error
    async def select__order_item(self, order_id):
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
