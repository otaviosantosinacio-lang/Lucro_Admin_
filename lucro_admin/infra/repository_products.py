import logging
from dataclasses import asdict

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger('lucroadmin.infra.repository.products')


class Products():

    def __init__(self, session: AsyncSession):
        self.session = session

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
            logger.info(
                'Lucro Admin Products | '
                'New products added'
            )
        except Exception as error:
            logger.warning(
                'Lucro Admin Products | '
                'Error saving the new products ->'
                ' Erro: %s',
                error
            )
            raise
