import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from lucro_admin.adapters.bling.bling_orders import GetUrlXML
from lucro_admin.core.entities_pedidos import ErrorHTTP, PageResult
from lucro_admin.core.entities_produtos import ConfigSku
from lucro_admin.core.imposto.entities_imposto import (
    ErrorParse,
    ProductWithTax,
    SalesTaxes,
    TaxReturn,
)
from lucro_admin.core.imposto.regras_fiscais import uf_without_fcp
from lucro_admin.core.imposto.tax_calculator import TaxCalculator
from lucro_admin.infra.repositorio_produtos import Produtos
from lucro_admin.services.service_http_request_base import (
    BaseRequestHTTP,
)

logger = logging.getLogger('lucroadmin.services.blingpedidos')


class TaxInvoicesBling:
    """
    ParseXML -> Parse do XML para extração de impostos
    """

    def __init__(self, access_token, adapter) -> None:
        self.access_token = access_token
        self.adapter = adapter
        self.service_base = BaseRequestHTTP(
            self.adapter, self.access_token
        )
        self.calculadora = TaxCalculator()
        self.base_url = 'https://api.bling.com.br/Api/v3'
        self.adapter_xml = GetUrlXML()

    def url_nf(self, id_nf) -> str:
        """
        url_nf

        :param self: Objeto
        :param id_nf: Id único gerado pelo Bling para identificação da NF
        :return: URL endpoint para requisição da NF
        :rtype: str
        """
        return f'{self.base_url}/nfe/{id_nf}'

    def get_taxes_bling(self, pedido, situacao) -> TaxReturn | Any:
        """
        get_xml -> Get do XML por endpoint Bling

        :param self: Objeto
        :param pedido: Pedido completo de onde será feito a extração dos
        impostos
        :param situacao: Situação do pedido dentro do Bling (Ex: Atendido)
        :return: Impostos por produtos e imposto total da venda
        :rtype: RetornoImpostos | Any
        """

        url: str = self.url_nf(pedido.nf_id)
        response: PageResult = self.service_base.organiza_get_request(url)

        if response.status == 'ok':
            data = response.data.get('data', [])
            url_xml = data['xml']
            xml = self.adapter_xml.request_xml(url_xml)
            logger.info('Bling get_xml | Xml extraído %s', xml)
            parse = self.parse_xml(
                xml=xml, id_bling=pedido.id_bling, situacao=situacao
            )
            if isinstance(parse, ErrorParse):
                parse = self.calculadora.tax_calculator(
                    items=pedido.items,
                    id_bling=pedido.id_bling,
                    sit=situacao,
                    uf_dest=pedido.uf_dest,
                )
            return parse
        if response.status == 'rated_limit':
            erro = ErrorHTTP(
                status=response.error['status'],
                error=response.error['body'],
                method='get_xml',
                class_name='ParseXML',
                module='parse_xml.py',
                endpoint=url,
                data=datetime.now(),
            )
            logger.error(
                'Bling get_xml |'
                ' Erro ao buscar informações na endpoint %s -> %s',
                url,
                erro.status,
            )

            return self.calculadora.tax_calculator(
                items=pedido.itens,
                id_bling=pedido.id_bling,
                sit=situacao,
                uf_dest=pedido.uf_dest,
            )

    def get_xml(self, url):
        response = self.adapter_xml.request_xml(url)
        return response
