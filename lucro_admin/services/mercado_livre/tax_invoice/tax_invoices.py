import logging

from lucro_admin.services.parse_xml import ParseXML
from lucro_admin.services.service_http_request_base import (
    BaseRequestHTTP,
    PageResult,
)

logger = logging.getLogger('lucroadmin.services.mercadolivre.taxinvoices')


class TaxInvoicesMeli:
    def __init__(self, access_token: str, adapter, user_id):
        self.access_token = access_token
        self.adapter = adapter
        self.user_id = user_id
        self.base_url = 'https://api.mercadolibre.com'
        self.base_request = BaseRequestHTTP(self.adapter, self.access_token)
        self.parse_xml = ParseXML()

    def get_taxes(self, orders_id: list[int]):

        logger.info(
            'Mercado Livre Tax Invoice | Starting Get Invoices'
        )

        meli_taxes = []

        for order in orders_id:
            url_order_invoice: str = (
                f'{self.base_url}/users/{self.user_id}/invoices/orders/{order}'
            )
            response: PageResult = self.base_request.organiza_get_request(
                url_order_invoice
            )

            status: str = response.data['status']
            xml_location: str = response.data[
                'attributes'
                ][
                'xml_location'
                ]

            xml: str = self.get_xml(
                xml_location=xml_location
            )

            taxes_order = self.parse_xml.parse_xml(
                xml=xml, order_id=order, situation=status)

    def get_xml(self, xml_location):

        url: str = f'{self.base_url}{xml_location}'

        response = self.adapter.get_endpoint(
                access_token=self.access_token,
                url=url
            )

        xml = response.text

        return xml
