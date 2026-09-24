import logging
from dataclasses import asdict

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from lucro_admin.infra.db_error_handle import handler_db_error

logger = logging.getLogger('lucroadmin.infra.repository.products')


class OrderPage():
    def __init__(self, session):
        self.session = session

    @handler_db_error
    async def select_last_order_page(self):
        query = text(
            '''
                WITH as more_order_page(
                    SELECT
                        COUNT(op.id):: INTEGER as pages
                    FROM order_page op
                    WHERE op.more_orders = 1
                    GROUP BY op.id
                )
                IF more_orde_page.pages > 0
                    SELECT
                        op.id,
                        op.date_page,
                        op.page,
                        op.more_orders
                    FROM order_page op
                    WHERE op.more_orders = 1
                ELSE
                    SELECT
                        op.id,
                        op.date_page,
                        op.page,
                        op.more_orders
                        MAX(op.updated_at):: DATE as last_update
                        SUM(op.page, 1):: INTEGER as next_page
                    FROM order_page op
            '''
        )
