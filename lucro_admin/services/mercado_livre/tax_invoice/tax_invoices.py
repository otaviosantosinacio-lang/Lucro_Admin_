import logging

logger = logging.getLogger('lucroadmin.services.mercadolivre.taxinvoices')


class TaxInvoiceMeli():
    def __init__(
            self,
            access_token,
            adapter
    ):
        self.access_token = access_token
        self.adapter = adapter
        self.base_url = 'https://api.mercadolibre.com'

    def get_tax_invoice_meli(
            self,
            orders_id: list[int]
    ):

        