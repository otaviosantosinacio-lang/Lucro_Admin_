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

logger = logging.getLogger('lucroadmin.infra.repository.products')


class Products():

    def __init__(self, session: AsyncSession):
        self.session = session

        # ==========================
        #           INSERT
        # ==========================

    async def insert_products(self, products):

        query = text(
            '''
                INSERT INTO products(
                    external_product_id,
                    sku,
                    product_description,
                    supplier,
                    cost_price,
                    origin,
                    ncm,
                    cest,
                    created_user_id,
                    updated_user_id
                )
                VALUES(
                    :external_product_id,
                    :sku,
                    :product_description,
                    :supplier,
                    :cost_price,
                    :origin,
                    :ncm,
                    :cest,
                    1,
                    1
                )
                ON CONFLICT (external_product_id) DO NOTHING;
            '''
        )
        try:
            values = [asdict(product) for product in products]

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

    async def consult_product_with_full_sku(self, full_sku: str):

        query = text(
            '''
                SELECT p.product_id, p.sku, p.cost_price
                FROM fulfillment_product fp
                INNER JOIN products p
                    ON fp.product_id = p.product_id
                WHERE fp.fulfillment_sku = :sku
            '''
        )

        values = {'sku': full_sku}

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

    async def consult_product_with_sku(self, sku: str):

        query = text(
            '''
                SELECT product_id, sku, cost_price
                FROM products
                WHERE sku = :sku
            '''
        )

        values = {'sku': sku}

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

    async def consult_pk_externalid_all_products(
            self,
            offset,
            limit: int = 100
        ):

        query = text(
            '''
                SELECT product_id, external_id
                FROM products
                ORDER BY product_id
                LIMIT :limit
                OFFSET :offset
            '''
        )

        values = {
            'limit': limit,
            'offset': offset
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
