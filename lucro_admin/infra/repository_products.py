import logging
from dataclasses import asdict

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from lucro_admin.infra.db_error_handle import handler_db_error

logger = logging.getLogger('lucroadmin.infra.repository.products')


class Products():

    def __init__(self, session: AsyncSession):
        self.session = session

        # ==========================
        #           INSERT
        # ==========================

    @handler_db_error
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
        values = [asdict(product) for product in products]

        await self.session.execute(query, values)

        logger.info('Lucro Admin Repository |'
        ' New %s products added.',
        len(values)
        )

        # ==========================
        #           SELECT
        # ==========================

    @handler_db_error
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

        result = await self.session.execute(query, values)
        data = result.fetchall()
        return data

    @handler_db_error
    async def consult_product_with_sku(self, sku: str):

        query = text(
            '''
                SELECT product_id, sku, cost_price
                FROM products
                WHERE sku = :sku
            '''
        )

        values = {'sku': sku}

        result = await self.session.execute(query, values)
        data = result.fetchall()
        return data

    @handler_db_error
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
        result = await self.session.execute(query, values)
        data = result.fetchall()
        return data
