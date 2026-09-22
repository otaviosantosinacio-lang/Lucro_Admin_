import logging

from lucro_admin.adapters.bling.bling_orders import GetUrlXML
from lucro_admin.core.imposto.entities_imposto import ErrorParse
from lucro_admin.infra.database import SessionLocal
from lucro_admin.infra.repository_order_item_tax import OrderItemTax
from lucro_admin.services.parse_xml import ParseXML

logger = logging.getLogger('lucroadmin.services.bling.item_tax')


class XMLItemTax:

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.adapter = GetUrlXML()
        self.parse_xml = ParseXML()

    def get_xml(self, url):
        response = self.adapter.request_xml(url)
        return response

    async def order_item_tax(self):

        async with SessionLocal() as session:
            repository = OrderItemTax(session=session)
            offset = 0
            more_page = True
            items_taxes = []
            while more_page:
                orders_xml = await repository.searching_xml(
                    offset=offset,
                    integration_id=1
                )

                for order_xml in orders_xml:
                    url_xml = order_xml[1]
                    xml = self.adapter.request_xml(url=url_xml)
                    order_items = await repository.searching_order_item(
                        order_id=order_xml[0]
                    )
                    taxes = self.parse_xml.parse_xml(
                        xml=xml, order_items=order_items
                    )

                    if isinstance(taxes, ErrorParse):
                        continue
                    else:
                        for tax in taxes:
                            items_taxes.append(tax)
                if len(orders_xml) < 100:
                    more_page = False
                else:
                    offset += 100

            await repository.insert_tax_items(items_tax=items_taxes)

            await session.commit()

            await session.close()
