MARKETPLACE_POR_LOJA = {
    204442078: 'Mercado Livre Full',
    204196269: 'Mercado Livre',
    204524203: 'Amazon FBA Classic',
    204348449: 'Amazon DBA',
    204911672: 'Shein',
    205075855: 'Sicredi',
    204367139: 'Loja Integrada',
    204351182: 'MagaLu',
    204433176: 'Shopee',
    204342864: 'Venda Direta',
}


def nome_marketplace(id_loja: int) -> str:
    """
    nome_marketplace -> O bling nos retorna a loja como um código, por isso
devemos trata-la para visualizarmos por nome.

    :param id_loja: Id da loja gerado pelo Bling
    :type id_loja: int
    :return: Nome da loja (Ex: Mercado Livre).
    :rtype: str
    """
    return MARKETPLACE_POR_LOJA.get(id_loja, 'Loja não identificada')
