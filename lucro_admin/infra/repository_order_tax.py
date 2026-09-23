import logging
from dataclasses import asdict

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from lucro_admin.infra.db_error_handle import handler_db_error

logger = logging.getLogger('lucroadmin.infra.repository.order_tax')


class OrderTax:

    def __init__(self, session: AsyncSession):
        self.session = session

        # ==========================
        #           INSERT
        # ==========================

    @handler_db_error
    async def insert_tax_invoice(self, invoices):

        query = text(
            '''
                INSERT INTO tax_invoice(
                    order_id,
                    url_xml,
                    serie,
                    key_access,
                    issue_date,
                    tax_invoice_value,
                    created_user_id,
                    updated_user_id
                )
                VALUES(
                    :order_id,
                    :url_xml,
                    :serie,
                    :key_access,
                    :issue_date,
                    :tax_invoice_value,
                    1,
                    1
                )
            '''
        )

        values = [asdict(invoice) for invoice in invoices]

        await self.session.execute(query, values)
        logger.info('Lucro Admin Repository |'
        ' New %s invoices added.',
        len(values)
        )

        # ==========================
        #           SELECT
        # ==========================

    @handler_db_error
    async def searching_invoice_ids(
            self,
            offset,
            situation,
            limit=100,
    ):

        query = text(
            '''
                SELECT
                    o.order_id,
                    o.external_invoice_id
                FROM orders o
                LEFT JOIN tax_invoice ti
                    ON o.order_id = ti.order_id
                WHERE o.integration_invoice_id = 1
                    AND ti.order_id IS NULL
                ORDER BY o.order_id
                OFFSET :offset
                LIMIT :limit
            '''
        )

        values = {
            'offset': offset,
            'limit': limit
        }

        result = await self.session.execute(query, values)
        data = result.fetchall()
        return data
