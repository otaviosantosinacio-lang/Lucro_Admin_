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

    async def get_marketplace(self, marketplace_id):

        query = text(
            '''
                SELECT marketplace_id
                FROM marketplaces
                WHERE marketplace_external_id = :marketplace_external_id
            '''
        )

        values = {'marketplace_external_id': marketplace_id}
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
