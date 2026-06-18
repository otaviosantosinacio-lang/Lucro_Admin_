import logging
from zoneinfo import ZoneInfo


def somandosecs(segundos):
    logger = logging.getLogger('lucroadmin.utils.time')
    from datetime import datetime, timedelta

    agora = datetime.now(tz=ZoneInfo('UTC'))
    expira = agora + timedelta(seconds=segundos)
    logger.info('Validade do access token calculada')
    return expira
