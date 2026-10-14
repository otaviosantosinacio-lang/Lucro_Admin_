import logging
from dataclasses import asdict

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from lucro_admin.core.entities import PageOrders
from lucro_admin.infra.db_error_handle import handler_db_error

logger = logging.getLogger('lucroadmin.infra.repository.products')


class OrderPage():
    def __init__(self, session: AsyncSession):
        self.session = session

        # ==========================
        #           INSERT
        # ==========================

    @handler_db_error
    async def insert_order_page(self, orders_page):

        query = text(
            '''
                INSERT INTO order_page(
                    date_page,
                    page,
                    more_orders,
                    situation_id,
                    integration_id
                )
                VALUES(
                    :date_page,
                    :page,
                    :more_orders,
                    :situation_id,
                    :integration_id
                )
            '''
        )

        values = [asdict(page) for page in orders_page]

        await self.session.execute(query, values)
        logger.info('Lucro Admin Repository |'
        ' New %s order page added.',
        len(values)
        )

        # ==========================
        #           INSERT
        # ==========================

    @handler_db_error
    async def update_order_page(self, orders_page):

        query = text(
            '''
                UPDATE order_page
                    SET
                        more_orders = :more_orders
                WHERE id = :id
            '''
        )

        values = [asdict(page) for page in orders_page]

        await self.session.execute(query, values)
        logger.info('Lucro Admin Repository |'
        ' Updated %s order page.',
        len(values)
        )

        # ==========================
        #           SELECT
        # ==========================

    @handler_db_error
    async def select_pending_order_page(
        self,
        situation_id: int,
        integration_id: int
        ):
        query = text(
            '''
                SELECT
                    op.id,
                    op.date_page,
                    op.situation_id,
                    op.integration_id
                FROM order_page op
                ORDER BY id DESC
            '''
        )

        values = {
            'situation_id': situation_id,
            'integration_id': integration_id
        }
        result = await self.session.execute(query, values)
        data = result.fetchone()
        if data is not None:
            return PageOrders(
                        id=data[0][0],
                        date_page=data[0][1],
                        situation_id=data[0][2],
                        integration_id=data[0][3]
                    )
        else:
            return PageOrders(
                id=0,
                date_page=
            )
