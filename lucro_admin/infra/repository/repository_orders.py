import logging
from dataclasses import asdict

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from lucro_admin.infra.db_error_handle import handler_db_error

logger = logging.getLogger('lucroadmin.infra.repository.orders')


class Orders():

    def __init__(self, session: AsyncSession):
        self.session = session

        # ==========================
        #           INSERT
        # ==========================

    @handler_db_error
    async def insert_order(self, orders):

        query = text(
            '''
                INSERT INTO orders(
                    external_id,
                    origin_id,
                    situation_id,
                    marketplace_id,
                    marketplace_order_id,
                    order_date,
                    created_user_id,
                    updated_user_id
                )
                VALUES(
                    :external_id,
                    :origin_id,
                    :situation_id,
                    :marketplace_id,
                    :marketplace_order_id,
                    :order_date,
                    1,
                    1
                )
                ON CONFLICT (external_id) DO NOTHING;
            '''
        )

        values = [asdict(order) for order in orders]
        await self.session.execute(query, values)
        logger.info(
                        'Lucro_Admin Orders | '
                        'New %s orders added',
                        len(values)
                    )

        # ==========================
        #           UPDATE
        # ==========================

    @handler_db_error
    async def insert_order_details(self, order_details):

        query = text(
            '''
                UPDATE orders
                    SET
                        external_invoice_id = :external_invoice_id,
                        value_order = :value_order,
                        uf_dest = :uf_dest,
                        transport = :transport,
                        updated_user_id = 1
                WHERE order_id = :order_id
            '''
        )

        values = [asdict(detail) for detail in order_details]
        await self.session.execute(query, values)
        logger.info('Lucro Admin Repository |'
        ' New %s order details added.',
        len(values)
        )
        # ==========================
        #           SELECT
        # ==========================

    @handler_db_error
    async def select_last_date_order(self):

        query = text(
            '''
                SELECT MAX(order_date)::DATE as last_order
                FROM orders

            '''
        )
        result = await self.session.execute(query)
        data = result.fetchall()
        return data

    @handler_db_error
    async def select_orders_without_details(
        self,
        offset,
        situation_id,
        limit=100
    ):

        query = text(
            '''
                SELECT order_id, external_id
                FROM orders
                WHERE value_order is NULL and situation_id = :situation_id
                ORDER BY order_id
                LIMIT :limit
                OFFSET :offset
            '''
        )

        values = {
            'situation_id': situation_id,
            'offset': offset,
            'limit': limit,
        }

        result = await self.session.execute(query, values)
        data = result.fetchall()
        return data
