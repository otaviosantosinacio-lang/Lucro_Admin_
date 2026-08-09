import logging
from dataclasses import asdict

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger('lucroadmin.infra.repository.bling_situations')


class BlingOrderSituation():

    def __init__(self, session: AsyncSession):
        self.session = session

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
        try:
            values = [asdict(situation) for situation in situations]
            await self.session.execute(query, values)
            logger.info(
                'Bling Orders Situation | '
                'New Bling orders situations added'
            )

        except Exception as error:
            logger.warning(
                'Bling Orders Situation | '
                'Error saving the new situations ->'
                ' Erro: %s',
                error
            )
            raise

    async def extract_situation(self, situation_name):

        query = text(
                '''
                SELECT situation_id, situation_bling_id,
                    situation_name, situation_color
                FROM bling_orders_situation
                WHERE situation_name = :situation_name
                '''
        )

        try:
            values = {'situation_name': situation_name}
            result = await self.session.execute(query, values)

            data = result.fetchall()
            print(data)

            return data
        except Exception as error:
            logger.warning(
                'Bling Orders Situation | '
                'Erro on extract ->'
                ' Erro: %s',
                error
            )
            raise
