from decimal import Decimal
import logging

logger = logging.getLogger('lucroadmin.core.regrasfiscais')

sem_fcp = {'AC', 'AP', 'PA', 'SC'}
icms = {
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
    icms_aliq

    Carregando aliquota ICMS mediante parametro UF

    :param UF: UF destino da venda
    :type UF: str
    :return: Valor da aliquota
    :rtype: Decimal
    """
    try:
        aliquota = icms.get(UF)
        logger.info(
            'Regras Fiscais | A aliquota ICMS da UF - %s - é de %s',
            UF,
            aliquota,
        )
        return aliquota
    except KeyError:
        logger.exception(
            'Regras Fiscais | Aliquota de ICMS não cadastrada para a UF - %s',
            UF,
        )
        raise ValueError(f'Aliquota de ICMS não cadastrada para a UF - {UF}')


def uf_sem_fcp(uf: str) -> bool:
    """
    uf_sem_fcp

    Função para descobrirmos quais estados não fazem cobrança do FCP

    :param uf: UF para verificação de cobrança ou não do FCP
    :type uf: str
    :return: True or False
    :rtype: bool
    """
    return uf in sem_fcp
