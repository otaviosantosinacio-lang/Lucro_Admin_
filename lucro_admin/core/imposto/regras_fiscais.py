import logging

logger = logging.getLogger('lucroadmin.core.regrasfiscais')

sem_fcp = {'AC', 'AP', 'PA', 'SC'}
icms: dict[str, int | float] = {
    'RS': 17,
    'SC': 17,
    'MT': 17,
    'ES': 17,
    'MS': 17,
    'MG': 18,
    'RN': 18,
    'AP': 18,
    'GO': 17,
    'PA': 19,
    'AL': 19,
    'SE': 19,
    'AC': 19,
    'PR': 19.5,
    'RO': 19.5,
    'DF': 20,
    'CE': 20,
    'AM': 20,
    'PB': 20,
    'TO': 20,
    'RR': 20,
    'BA': 20.5,
    'PE': 20.5,
    'PI': 21,
    'RJ': 22,
    'MA': 22,
}


def icms_aliq(UF: str) -> float | int:
    """
    icms_rate

    Loading ICMS rate based on the state parameter

    :param UF: Destination state of the sale
    :type UF: str
    :return: Rate value
    :rtype: float | int
    """
    try:
        rate: int | float = icms.get(UF)
        logger.info(
            'Tax Rules | The ICMS rate of the state - %s - is %s',
            UF,
            rate,
        )
        return rate
    except KeyError:
        logger.exception(
            'Tax Rules | ICMS rate not registered for the state - %s',
            UF,
        )
        raise ValueError(f'ICMS rate not registered for the state - {UF}')


def uf_without_fcp(uf: str) -> bool:
    """
    uf_without_fcp

    Function to determine which states do not charge the FCP

    :param uf: State abbreviation to check whether it charges the FCP or not
    :type uf: str
    :return: True or False
    :rtype: bool
    """
    return uf in sem_fcp
