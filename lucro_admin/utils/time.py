import logging


def somandosecs(segundos):
    logger = logging.getLogger('lucroadmin.utils.time')
    from datetime import datetime, timedelta

    agora = datetime.now()
    expira = agora + timedelta(seconds=segundos)
    logger.info('Validade do access token calculada')
    return expira
