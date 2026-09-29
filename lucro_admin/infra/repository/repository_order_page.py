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
                WITH pending_pages AS(
                    SELECT
                        op.id,
                        op.date_page,
                        op.page,
                        op.more_orders,
                        op.situation_id,
                        op.integration_id
                    FROM order_page op
                    WHERE op.more_orders = TRUE
                        AND op.situation_id = :situation_id
                        AND op.integration_id = :integration_id
                ),
                next_start AS(
                    SELECT
                        NULL::INTEGER AS id,
                        COALESCE(
                            MAX(op.updated_at)::DATE, CURRENT_DATE
                            ) AS date_page,
                        1 AS page,
                        TRUE AS more_page.
                        :situation_id AS situation_id,
                        :integration_id AS integration_id
                    FROM order_page op
                    WHERE op.situation_id = :situation_id
                        AND op.integration_id = :integration_id
                )
                SELECT * FROM pending_pages
                UNION ALL
                SELECT * FROM next_start
                WHERE NOT EXITIS (SELECT 1 FROM pending_pages);
            '''
        )

        values = {
            'situation_id': situation_id,
            'integration_id': integration_id
        }
        result = await self.session.execute(query, values)
        data = result.fetchall()
        return PageOrders(
                    id=data[0][0],
                    date_page=data[0][1],
                    page=data[0][2],
                    more_orders=data[0][3],
                    situation_id=data[0][4],
                    integration_id=data[0][5]
                )
