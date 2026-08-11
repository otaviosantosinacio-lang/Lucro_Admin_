import logging
from dataclasses import asdict

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger('lucroadmin.infra.repository.orders')


class Orders():

    def __init__(self, session: AsyncSession):
        self.session = session

    async def last_date_order(self):

        query = text(
            '''
                SELECT MAX(created_at)::DATE as last_order
                FROM orders

            '''
        )

        result = await self.session.execute(query)

        data = result.fetchall()

        return data

    async def orders_without_details(self, offset, situation_id, limit=100):

        query = text(
            '''
                SELECT order_id, external_id
                FROM orders
                ORDER BY order_id
                WHERE value_order is NULL and situation_id = :situation_id
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

        try:
            values = [asdict(order) for order in orders]
            await self.session.execute(query, values)
            logger.info(
                            'Lucro_Admin Orders | '
                            'New %s orders added',
                            len(values)
                        )

        except Exception as error:
            logger.warning(
                'Lucro_Admin Orders | '
                'Error saving the new orders ->'
                ' Erro: %s',
                error
                    )
            raise
