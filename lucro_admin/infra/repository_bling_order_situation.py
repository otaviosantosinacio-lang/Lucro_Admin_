import logging
from dataclasses import asdict

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from lucro_admin.infra.db_error_handle import handler_db_error

logger = logging.getLogger('lucroadmin.infra.repository.bling_situations')


class BlingOrderSituation():

    def __init__(self, session: AsyncSession):
        self.session = session

        # ==========================
        #           INSERT
        # ==========================

    @handler_db_error
    async def insert_situations(self, situations):

        query = text(
            '''
                INSERT INTO bling_orders_situation(
                    situation_bling_id,
                    situation_name,
                    situation_color
                )
                VALUES(
                    :situation_bling_id,
                    :situation_name,
                    :situation_color
                )
                ON CONFLICT (situation_bling_id) DO NOTHING;
            '''
        )

        values = [asdict(situation) for situation in situations]

        await self.session.execute(query, values)
        logger.info(
            'Bling Orders Situation | '
            'New %s Bling orders situations added',
            len(values)
        )

        # ==========================
        #           SELECT
        # ==========================

    @handler_db_error
    async def extract_situation(self, situation_name):

        query = text(
                '''
                SELECT situation_id, situation_bling_id,
                    situation_name, situation_color
                FROM bling_orders_situation
                WHERE situation_name = :situation_name
                '''
        )

        values = {'situation_name': situation_name}

        result = await self.session.execute(query, values)
        data = result.fetchall()
        return data
