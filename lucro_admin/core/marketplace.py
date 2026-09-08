from dataclasses import dataclass

slug_marketplace_ = {
    'MercadoLivre': 'mercado_livre',
    'Amazon': 'amazon',
    'LojaFisica': 'loja_fisica',
    'Api': 'api',
    'Olist': 'olist',
    'ViaVarejo': 'via_varejo',
    'IntegraCommerce': 'magalu',
    'LojaIntegrada': 'loja_integrada',
    'AmazonFulfillment': 'amazon_fba',
    'AmazonFBAClassic': 'amazon_fba_classic',
    'Shopee': 'shopee',
    'Shein': 'shein',
    'Sicredi': 'sicredi',
    'TikTok': 'tik_tok',
    'MadeiraMadeira': 'madeira_madeira'
}


def slug_marketplace(external_type: int) -> str:
    """
        nome_marketplace -> O bling nos retorna a loja como um código, por isso
    devemos trata-la para visualizarmos por nome.

        :param id_loja: Id da loja gerado pelo Bling
        :type id_loja: int
        :return: Nome da loja (Ex: Mercado Livre).
        :rtype: str
    """
    return slug_marketplace_.get(external_type, 'Loja não identificada')


@dataclass
class Marketplace:
    marketplace_external_id: int
    external_type: str
    marketplace_name: str
    status: bool
    slug: str
