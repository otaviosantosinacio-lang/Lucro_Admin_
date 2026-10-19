import logging
from dataclasses import asdict

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from lucro_admin.core.marketplace import MarketplaceIntegration
from lucro_admin.infra.db_error_handle import handler_db_error

logger = logging.getLogger('lucroadmin.infra.repository.marketplaces')


class Marketplaces():
    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session

        # ==========================
        #           INSERT
        # ==========================

    @handler_db_error
    async def insert_marketplaces(self, marketplaces):

        query = text(
            '''
                INSERT INTO marketplaces(
                    marketplace_external_id,
                    external_type,
                    marketplace_name,
                    status,
                    integration_erp,
                    integration_marketplace,
                    created_user_id,
                    updated_user_id
                )
                VALUES(
                    :marketplace_external_id,
                    :external_type,
                    :marketplace_name,
                    :status,
                    :integration_erp,
                    :integration_marketplace,
                    1,
                    1
                )
                ON CONFLICT (marketplace_external_id) DO NOTHING;
            '''
        )

        values = [asdict(marketplace) for marketplace in marketplaces]
        await self.session.execute(query, values)
        logger.info(
                        'Lucro_Admin Marketplaces | '
                        'New %s Marketplaces added',
                        len(values)
                    )

        # ==========================
        #           SELECT
        # ==========================

    @handler_db_error
    async def select_marketplace(self, marketplace_id):

        query = text(
            '''
                SELECT
                    marketplace_id
                FROM marketplaces
                WHERE marketplace_external_id = :marketplace_external_id
            '''
        )

        values = {'marketplace_external_id': marketplace_id}
        result = await self.session.execute(query, values)
        data = result.fetchall()
        return data

    @handler_db_error
    async def select_integration_marketplace(self):

        query = text(
            '''
                SELECT
                    integrations.integration_id,
                    integrations.name
                FROM integrations
            '''

        )

        result = await self.session.execute(query)
        data = result.fetchall()

        return data

    @handler_db_error
    async def select_integration_cost(self, orders_id):

        query = text(
            '''
                SELECT
                    o.order_id,
                    mkt.integration_marketplace
                FROM orders o
                INNER JOIN marketplaces mkt
                    ON o.marketplace_id = mkt.marketplace_id
                WHERE o.order_id = ANY (:orders_id)
                    AND mkt.integration_marketplace IS NOT NULL
            '''
        )

        values = {
            'orders_id': orders_id
        }

        result = await self.session.execute(query, values)

        return [
            MarketplaceIntegration(
                order_id=row[0],
                integration_id=row[1]
                ) for row in result.fetchall()]
