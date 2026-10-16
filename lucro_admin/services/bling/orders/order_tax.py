import logging
from typing import Any

from lucro_admin.adapters.bling.bling_orders import CrudBling
from lucro_admin.core.imposto.entities_imposto import InsertTaxInvoice
from lucro_admin.infra.repository.repository_order_tax import OrderTax
from lucro_admin.infra.repository.repository_pipeline_execution import (
    PipelineExecution,
)
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

logger = logging.getLogger('lucroadmin.services.ordertax')


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
        get_invoice_blin -> Get invoice details bling endpoint

        This pipeline stage insert in database invoice tax details.

        :param session: Database Session
        """

        repository = OrderTax(session=session)
        repository_pipeline = PipelineExecution(session=session)

        offset: int = 0
        more_page: bool = True
        tax_invoices = []
        pipeline_update = []

        while more_page:
            pipeline_id = await repository_pipeline.select_pipeline_execution(
                stage_id=2,
                status_id=2,
                offset=offset,
                integration_id=1
            )

            for pipeline in pipeline_id:
                invoice_id = await repository.select_invoice_ids(
                    order_id=pipeline[1]
                )
                if invoice_id != 0:
                    url: str = self.url_nf(invoice_id[1])
                    response = self.service_base.organiza_get_request(url)

                    if response.status == 'ok':
                        data = response.data.get('data', [])
                        tax_invoices.append(
                            InsertTaxInvoice(
                                order_id=invoice_id[0],
                                url_xml=data['xml'],
                                serie=data['serie'],
                                key_access=data['chaveAcesso'],
                                issue_date=data['dataEmissao'],
                                tax_invoice_value=data['valorNota'],
                            )
                        )
                        pipeline_update.append(
                            {
                                'pipeline_id': pipeline[0],
                                'order_id': pipeline[1],
                                'status_id': 1
                            }
                        )
                    else:
                        logger.error(
                            'Bling get_xml |'
                        ' Error request %s -> %s',
                            url,
                            response.error,
                        )
            if len(pipeline_id) < 100:
                more_page = False
            else:
                offset += 100
                continue
        await repository.insert_tax_invoice(invoices=tax_invoices)

        await repository_pipeline.update_pipeline_execution(
            pipeline_ids=pipeline_update
        )
        await repository_pipeline.insert_pipeline_execution(
            orders_id=[(order['order_id']) for order in pipeline_update],
            stage_id=3,
            status_id=2,
            integration_id=1
        )

        await repository_pipeline.update_pipeline_execution(pipeline_update)

        await session.commit()

        logger.info(
            'Bling get_invoice_bling |'
            ' New tax invoices added in database -> Qnt %s',
            len(tax_invoices),
                        )
