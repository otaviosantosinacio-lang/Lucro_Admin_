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
                ON CONFLICT (external_id) DO NOTHING
                RETURNING order_id;
            '''
        )

        values = [asdict(order) for order in orders]
        result = await self.session.execute(query, values)
        logger.info(
                        'Lucro_Admin Orders | '
                        'New %s orders added',
                        len(values)
                    )

        data = result.fetchall()

        return data

        # ==========================
        #           UPDATE
        # ==========================

    @handler_db_error
    async def update_order_details(self, order_details):

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
    async def select_order_id(self, order_id):
        query = text(
            '''
                SELECT
                    order_id,
                    external_id
                FROM orders
                WHERE order_id = :order_id
            '''
        )

        values = {
            'order_id': order_id
        }

        result = await self.session.execute(query, values)

        data = result.fetchall()

        return data
