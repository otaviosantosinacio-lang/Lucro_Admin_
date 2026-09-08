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

logger = logging.getLogger('lucroadmin.infra.repository.order_item_tax')


class OrderItemTax:

    def __init__(self, session: AsyncSession):
        self.session = session

        # ==========================
        #           INSERT
        # ==========================

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

    async def searching_xml(
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

    async def searching_order_item(self, order_id):
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
