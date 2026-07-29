import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def somandosecs(segundos):
    logger = logging.getLogger('lucroadmin.utils.time')

    agora = datetime.now(tz=ZoneInfo('America/Sao_Paulo'))
    expira = agora + timedelta(seconds=segundos)
    logger.info(
        'Validade do access token calculada ->'
        ' Agora %s -> Expiração %s', agora, expira
    )
    return expira
