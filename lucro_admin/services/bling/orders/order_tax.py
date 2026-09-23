import logging
from datetime import datetime
from typing import Any

from lucro_admin.adapters.bling.bling_orders import CrudBling
from lucro_admin.core.entities_pedidos import ErrorHTTP
from lucro_admin.core.imposto.entities_imposto import InsertTaxInvoice
from lucro_admin.infra.repository_order_tax import OrderTax
from lucro_admin.services.bling.credentials.providers.bling_provider import (
    BlingProvider,
)
from lucro_admin.services.bling.orders.order_situation_bling import (
    OrderSituationBling,
)
from lucro_admin.services.service_http_request_base import (
    BaseRequestHTTP,
)
from lucro_admin.services.token_service import TokenService

logger = logging.getLogger('lucroadmin.services.blingpedidos')


class TaxInvoicesBling:

    def __init__(self) -> None:
        self.provider = BlingProvider()
        self.token_service = TokenService(self.provider)
        self.access_token = self.token_service.validate_access_token()
        self.adapter = CrudBling()
        self.service_base = BaseRequestHTTP(
            self.adapter, self.access_token
        )
        self.base_url = 'https://api.bling.com.br/Api/v3'
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

    async def get_invoice_bling(self, session) -> Any:
        """
        get_xml -> Get do XML por endpoint Bling

        :param self: Objeto
        :param pedido: Pedido completo de onde será feito a extração dos
        impostos
        :param situacao: Situação do pedido dentro do Bling (Ex: Atendido)
        :return: Impostos por produtos e imposto total da venda
        :rtype: RetornoImpostos | Any
        """

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

        logger.info(
            'Bling get_invoice_bling |'
            ' New tax invoices added in database -> Qnt %s',
            len(tax_invoices),
                        )
