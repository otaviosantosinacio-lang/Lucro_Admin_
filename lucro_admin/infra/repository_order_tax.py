import logging
from dataclasses import asdict

from sqlalchemy import text
from sqlalchemy.exc import (
    DataError,
    IntegrityError,
    OperationalError,
    SQLAlchemyError,
)
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger('lucroadmin.infra.repository.order_tax')


class OrderTax:

    def __init__(self, session: AsyncSession):
        self.session = session

        # ==========================
        #           INSERT
        # ==========================

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

        try:
            await self.session.execute(query, values)
            logger.info('Lucro Admin Repository |'
            ' Database transaction completed.')

        except OperationalError as conn_error:
            await self.session.rollback()
            logger.critical('Lucro Admin Repository | '
            'Database connection error. -> Error = %s',
            conn_error
            )
            raise

        except IntegrityError as integ_error:
            await self.session.rollback()
            logger.critical('Lucro Admin Repository | '
            'Data integrity violation (Duplicate record or invalid FK). '
            '-> Error = %s',
            integ_error
            )
            raise

        except SQLAlchemyError as db_error:
            await self.session.rollback()
            logger.critical('Lucro Admin Repository | '
            'Unexpected error in the database. '
            '-> Error = %s',
            db_error
            )
            raise

        except Exception as unexpected_error:
            await self.session.rollback()
            logger.critical('Lucro Admin Repository | '
            'Unmapped systemic error. '
            '-> Error = %s',
            unexpected_error
            )
            raise

        # ==========================
        #           SELECT
        # ==========================

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

        try:
            result = await self.session.execute(query, values)
            data = result.fetchall()
            return data

        except OperationalError as conn_error:
            await self.session.rollback()
            logger.critical('Lucro Admin Repository | '
            'Database connection error. -> Error = %s',
            conn_error
            )
            raise

        except DataError as data_error:
            await self.session.rollback()
            logger.critical('Lucro Admin Repository | '
            'Type error in the data sent in the query. '
            '-> Error = %s',
            data_error
            )
            raise

        except SQLAlchemyError as db_error:
            await self.session.rollback()
            logger.critical('Lucro Admin Repository | '
            'Unexpected error in the database. '
            '-> Error = %s',
            db_error
            )
            raise

        except Exception as unexpected_error:
            await self.session.rollback()
            logger.critical('Lucro Admin Repository | '
            'Unmapped systemic error. '
            '-> Error = %s',
            unexpected_error
            )
            raise
