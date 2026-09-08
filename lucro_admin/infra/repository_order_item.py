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

logger = logging.getLogger('lucroadmin.infra.repository.order_item')


class OrderItem:

    def __init__(self, session: AsyncSession):
        self.session = session

        # ==========================
        #           INSERT
        # ==========================

    async def insert_ordem_item(self, order_items):
        query = text(
            '''
                INSERT INTO order_item (
                    order_id,
                    situation_id,
                    product_id,
                    quantity,
                    cost_price,
                    unit_selling_price,
                    created_user_id,
                    updated_user_id
                )
                VALUES(
                    :order_id,
                    :situation_id,
                    :product_id,
                    :quantity,
                    :cost_price,
                    :unit_selling_price,
                    1,
                    1
                )
            '''
        )

        values = [asdict(order_item) for order_item in order_items]

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
        #           UPDATE
        # ==========================

    async def update_shipping_commission(self, items):
        query = text(
            '''
                UPDATE order_item
                    SET
                        item_shipping = :item_shipping,
                        item_commission = :item_commission
                WHERE order_item_id = :order_item_id
            '''
        )

        values = [asdict(item) for item in items]

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

    async def item_without_commission_meli(
            self,
            offset,
            limit=100
            ):
        query = text(
            '''
                SELECT
                    o.order_id,
                    o.marketplace_order_id,
                    o.transport,
                    mkt.slug
                FROM orders o
                INNER JOIN marketplaces mkt
                    ON o.marketplace_id = mkt.marketplace_id
                LEFT JOIN order_item oi
                    ON o.order_id = oi.order_id
                WHERE oi.item_commission IS NULL
                    AND mkt.slug = 'mercado_livre'
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
