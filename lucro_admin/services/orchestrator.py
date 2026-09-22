from lucro_admin.services.bling.orders.orders import Attended, OrderDetails


class PipeLineOrchestrator:

    async def execute(self):
        await self.order_pipeline()
        await self.order_details_pipeline()
        await self.fiscal_pipeline()
        await self.order_costs_pipeline()

    async def order_pipeline(self):
        orders = Attended()
        await orders.get_id_by_page()

    async def order_details_pipeline(self):
        pass

    async def fiscal_pipeline(self):
        pass

    async def order_costs_pipeline(self):
        pass
