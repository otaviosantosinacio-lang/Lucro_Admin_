import logging
from dataclasses import asdict

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

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
                    created_user_id,
                    updated_user_id
                )
                VALUES(
                    :marketplace_external_id,
                    :external_type,
                    :marketplace_name,
                    :status,
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
    async def get_marketplace(self, marketplace_id):

        query = text(
            '''
                SELECT marketplace_id
                FROM marketplaces
                WHERE marketplace_external_id = :marketplace_external_id
            '''
        )

        values = {'marketplace_external_id': marketplace_id}
        result = await self.session.execute(query, values)
        data = result.fetchall()
        return data
