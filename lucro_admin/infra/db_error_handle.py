import logging
from functools import wraps

from sqlalchemy.exc import (
    DataError,
    IntegrityError,
    OperationalError,
    SQLAlchemyError,
)

logger = logging.getLogger('lucroadmin.infra.handlerdberror')


def handler_db_error(func):

    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)

        except OperationalError as conn_error:
            await self.session.rollback()
            logger.critical('Lucro Admin Repository | %s | '
            'Database connection error. -> Error = %s',
            func.__name__, conn_error
            )
            raise

        except IntegrityError as integ_error:
            await self.session.rollback()
            logger.critical('Lucro Admin Repository | %s | '
            'Data integrity violation (Duplicate record or invalid FK). '
            '-> Error = %s',
            func.__name__, integ_error
            )
            raise

        except DataError as data_error:
            await self.session.rollback()
            logger.critical('Lucro Admin Repository | %s | '
            'Type error in the data sent in the query. '
            '-> Error = %s',
            func.__name__, data_error
            )
            raise

        except SQLAlchemyError as db_error:
            await self.session.rollback()
            logger.critical('Lucro Admin Repository | %s | '
            'Unexpected error in the database. '
            '-> Error = %s',
            func.__name__, db_error
            )
            raise

        except Exception as unexpected_error:
            await self.session.rollback()
            logger.critical('Lucro Admin Repository | %s| '
            'Unmapped systemic error. '
            '-> Error = %s',
            func.__name__, unexpected_error
            )
            raise
