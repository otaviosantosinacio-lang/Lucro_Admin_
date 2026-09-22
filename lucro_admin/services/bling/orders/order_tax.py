import logging
from datetime import datetime
from typing import Any

from lucro_admin.adapters.bling.bling_orders import GetUrlXML
from lucro_admin.core.entities_pedidos import ErrorHTTP
from lucro_admin.core.imposto.entities_imposto import InsertTaxInvoice
from lucro_admin.infra.database import SessionLocal
from lucro_admin.infra.repository_order_tax import OrderTax
from lucro_admin.services.bling.orders.order_situation_bling import (
    OrderSituationBling,
)
from lucro_admin.services.parse_xml import ParseXML
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
        self.base_url = 'https://api.bling.com.br/Api/v3'
        self.adapter_xml = GetUrlXML()
        self.parse_xml = ParseXML()
        self.order_situation = OrderSituationBling(
            adapt_order=self.adapter,
            access_token=self.access_token
        )

    def url_nf(self, id_nf) -> str:
        """
        url_nf

        :param self: Objeto
        :param id_nf: Id único gerado pelo Bling para identificação da NF
        :return: URL endpoint para requisição da NF
        :rtype: str
        """
        return f'{self.base_url}/nfe/{id_nf}'

    async def get_invoice_bling(self) -> Any:
        """
        get_xml -> Get do XML por endpoint Bling

        :param self: Objeto
        :param pedido: Pedido completo de onde será feito a extração dos
        impostos
        :param situacao: Situação do pedido dentro do Bling (Ex: Atendido)
        :return: Impostos por produtos e imposto total da venda
        :rtype: RetornoImpostos | Any
        """

        async with SessionLocal() as session:
            repository = OrderTax(session=session)
            sit = await self.order_situation.situation_data_base(
                situation='Atendido'
            )

            offset: int = 0
            more_page: bool = True
            tax_invoices = []

            while more_page:
                invoice_ids = await repository.searching_invoice_ids(
                    offset=offset,
                    situation=sit.situation_bling_id,
                    limit=100
                )

                if len(invoice_ids) > 0:
                    for invoice in invoice_ids:
                        url: str = self.url_nf(invoice[1])
                        response = self.service_base.organiza_get_request(url)

                        if response.status == 'ok':
                            data = response.data.get('data', [])
                            tax_invoices.append(
                                InsertTaxInvoice(
                                    order_id=invoice[0],
                                    url_xml=data['xml'],
                                    serie=data['serie'],
                                    key_access=data['chaveAcesso'],
                                    issue_date=data['dataEmissao'],
                                    tax_invoice_value=data['valorNota'],
                                )
                            )
                            '''
                            url_xml = data['xml']
                            xml = self.adapter_xml.request_xml(url_xml)
                            logger.info('Bling get_xml | Xml extraído %s', xml)
                            parse = self.parse_xml.parse_xml(
                        xml=xml, order_id=pedido.id_bling, situation=situacao
                            )
                            return parse'''
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
                if len(invoice_ids) < 100:
                    more_page = False
                else:
                    offset += 100
                    continue
            await repository.insert_tax_invoice(invoices=tax_invoices)

            await session.commit()
            await session.close()

            logger.info(
                'Bling get_invoice_bling |'
                ' New tax invoices added in database -> Qnt %s',
                len(tax_invoices),
                            )

    def get_xml(self, url):
        response = self.adapter_xml.request_xml(url)
        return response
