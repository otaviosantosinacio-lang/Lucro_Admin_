import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def somandosecs(segundos):
    logger = logging.getLogger('lucroadmin.utils.time')

    agora = datetime.now(tz=ZoneInfo('UTC'))
    expira = agora + timedelta(seconds=segundos)
    logger.info('Validade do access token calculada')
    return expira
