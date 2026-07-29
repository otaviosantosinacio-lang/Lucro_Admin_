import logging

from lucro_admin.services.parse_xml import ParseXML
from lucro_admin.services.service_http_request_base import BaseRequestHTTP

logger = logging.getLogger('lucroadmin.services.mercadolivre.taxinvoices')


class TaxInvoicesMeli:
    def __init__(self, access_token: str, adapter, user_id):
        self.access_token = access_token
        self.adapter = adapter
        self.user_id = user_id
        self.base_url = 'https://api.mercadolibre.com'
        self.base_request = BaseRequestHTTP(self.adapter, self.access_token)
        self.parse_xml = ParseXML()
    def get_tax_invoice(self, orders_id: list[int]):

        logger.info(
            'Mercado Livre Tax Invoice | Starting Get Invoices'
        )

        meli_taxes = []

        for order in orders_id:
            url_order_invoice: str = (
                f'{self.base_url}/users/{self.user_id}/invoices/orders/{order}'
            )
            response_order = self.base_request.organiza_get_request(
                url_order_invoice
            )

            xml_location: str = response_order.data[
                'attributes'
                ][
                'xml_location'
                ]
            url_xml = f'{self.base_url}{xml_location}'

            response_xml = self.adapter.get_endpoint(
                access_token=self.access_token, url=url_xml
            )

            taxes_order = self.parse_xml.parse_xml(
                xml=response_xml.text)