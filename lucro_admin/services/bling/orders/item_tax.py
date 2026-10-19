import logging

from lucro_admin.adapters.bling.bling_orders import GetUrlXML
from lucro_admin.core.imposto.entities_imposto import ErrorParse
from lucro_admin.infra.repository.repository_marketplaces import Marketplaces
from lucro_admin.infra.repository.repository_order_item_tax import OrderItemTax
from lucro_admin.infra.repository.repository_pipeline_execution import (
    PipelineExecution,
)
from lucro_admin.services.bling.credentials.providers.bling_provider import (
    BlingProvider,
)
from lucro_admin.services.parse_xml import ParseXML
from lucro_admin.services.token_service import TokenService

logger = logging.getLogger('lucroadmin.services.bling.item_tax')


class XMLItemTax:

    def __init__(self):
        self.provider = BlingProvider()
        self.token_service = TokenService(self.provider)
        self.access_token = self.token_service.validate_access_token()
        self.adapter = GetUrlXML()
        self.parse_xml = ParseXML()

    def get_xml(self, url):
        response = self.adapter.request_xml(url)
        return response

    async def order_item_tax(self, session):
        repository_tax_item = OrderItemTax(session=session)
        repository_pipeline = PipelineExecution(session=session)
        offset = 0
        more_page = True
        items_taxes = []
        pipeline_update = []
        while more_page:
            pipeline_ids = await repository_pipeline.select_pipeline_execution(
                stage_id=3,
                status_id=2,
                integration_id=1,
                offset=offset
            )

            for pipeline in pipeline_ids:
                invoice = await repository_tax_item.select_xml_url(pipeline[1])
                url_xml = invoice[1]
                xml = self.adapter.request_xml(url=url_xml)
                order_items = await repository_tax_item.select_order_item(
                    order_id=pipeline[1]
                )
                taxes = self.parse_xml.parse_xml(
                    xml=xml, order_items=order_items
                )

                if isinstance(taxes, ErrorParse):
                    continue
                else:
                    for tax in taxes:
                        items_taxes.append(tax)
                    pipeline_update.append(
                        {
                            'pipeline_id': pipeline[0],
                            'order_id': pipeline[1],
                            'status_id': 1
                        }
                    )
            if len(pipeline_ids) < 100:
                more_page = False
            else:
                offset += 100

        await repository_tax_item.insert_tax_items(items_tax=items_taxes)

        await repository_pipeline.update_pipeline_execution(
            pipeline_ids=pipeline_update
        )

        await session.commit()
