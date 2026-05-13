import logging
from typing import Any
from dotenv import load_dotenv
import os
from pathlib import Path

from lucro_admin.adapters.mercado_pago.mercado_pago_get import GetMercadoPago
from lucro_admin.services.mercado_pago.service_mercadopago_base import (
    BaseHTTPMercadoPago,
)

logger = logging.getLogger('lucroadmin.services.mercadopago')


class MercadoPagoCustos:
    def __init__(self):
        BASE_DIR = Path(__file__).resolve().parents[2]
        load_dotenv(BASE_DIR / 'mp.env')
        access_token = os.getenv('access_token')
        self.access_token = access_token
        self.adapt_pedidos = GetMercadoPago()
        self.service_base = BaseHTTPMercadoPago(
            self.adapt_pedidos, self.access_token
        )

    def url_merchant(self, id_pay) -> str:

        url: str = f'https://api.mercadopago.com/v1/payments/{id_pay}'
        return url

    def get_merchant_orders(self, id_pay) -> float:

        url: str = self.url_merchant(id_pay=id_pay)

        response = self.service_base.organiza_get_request(url=url)

        json_value = ['shipping', 'fee']

        charges_details = response.data['charges_details']

        frete: float = 0.0

        logger.info('Mercado Pago Merchant Orders | %s', response.data)

        for key in charges_details:
            if key['type'] == 'shipping':
                frete = key['amounts']['original']
        logger.info('Mercado Pago Merchant Orders | Frete %s', frete)

        return frete
