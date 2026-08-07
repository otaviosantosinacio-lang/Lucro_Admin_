import logging
from dataclasses import asdict

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from lucro_admin.infra.database import get_session

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

            values = [asdict(situation) for situation in situations]
            self.session.execute(query, values)
            self.session.commit()
            logger.info(
                'Bling Orders Situation | '
                'New Bling orders situations added'
            )

        except Exception as error:
            self.session.rollback()
            logger.warning(
                'Bling Orders Situation | '
                'Error saving the new statuses ->'
                ' Erro: %s',
                error
            )
