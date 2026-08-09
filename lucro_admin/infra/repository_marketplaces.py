import logging
from dataclasses import asdict

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger('lucroadmin.infra.repository.marketplaces')


class Marketplaces():
    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session

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

        try:
            values = [asdict(marketplace) for marketplace in marketplaces]
            await self.session.execute(query, values)
            logger.info(
                            'Lucro_Admin Marketplaces | '
                            'New Marketplaces added'
                        )
        except Exception as error:
            logger.warning(
                'Lucro_Admin Marketplaces | '
                'Error saving the new marketplaces ->'
                ' Erro: %s',
                error
                    )
            raise

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
