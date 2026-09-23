from lucro_admin.infra.database import SessionLocal
from lucro_admin.services.bling.orders.item_tax import XMLItemTax
from lucro_admin.services.bling.orders.order_tax import TaxInvoicesBling
from lucro_admin.services.bling.orders.orders import Attended, OrderDetails
from lucro_admin.services.mercado_livre.pedidos.mercadolivre_pedidos import (
    ExtraiCustoMeli,
)


class PipelineOrchestrator:

    def __init__(self):
        self.orders = Attended()
        self.order_details = OrderDetails()
        self.order_tax = TaxInvoicesBling()
        self.item_tax = XMLItemTax()
        self.costs = ExtraiCustoMeli()

    async def execute(self):
        async with SessionLocal() as session:
            await self.order_pipeline(session)
            await self.order_details_pipeline(session)
            await self.fiscal_pipeline(session)
            await self.order_costs_pipeline(session)

    async def order_pipeline(self, session):
        await self.orders.get_id_by_page(session)

    async def order_details_pipeline(self, session):
        await self.order_details.get_id_details(session)

    async def fiscal_pipeline(self, session):
        await self.order_tax.get_invoice_bling(session)
        await self.item_tax.order_item_tax(session)

    async def order_costs_pipeline(self, session):
        await self.costs.get_sale_costs(session)
