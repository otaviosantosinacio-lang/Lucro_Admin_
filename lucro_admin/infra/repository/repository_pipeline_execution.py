import logging
from dataclasses import asdict

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from lucro_admin.infra.db_error_handle import handler_db_error

logger = logging.getLogger('lucroadmin.infra.repository.pipelineex')


class PipelineExecution:

    def __init__(self, session: AsyncSession):
        self.session = session

        # ==========================
        #           INSERT
        # ==========================

    @handler_db_error
    async def insert_pipeline_execution(
        self,
        orders_id,
        stage_id,
        status_id,
        integration_id
    ):

        query = text(
            '''
                INSERT INTO pipeline_execution(
                    order_id,
                    stage_id,
                    status_id,
                    integration_ind
                    attempts,
                    description
                )
                VALUES(
                    :order_id,
                    :stage_id,
                    :status_id,
                    :integration_id
                    0,
                    'PipeLine'
                )
                ON CONFLICT (uq_order_for_stage) DO NOTHING
                RETURNING pipeline_id
            '''
        )

        values = [
            {
                'order_id': order,
                'stage_id': stage_id,
                'status_id': status_id,
                'integration_id': integration_id}
            for order in orders_id
            ]

        result = await self.session.execute(query, values)

        data = result.fetchall()
        logger.info(
            'Lucro Admin Repository | '
            'Insert %s new pipeline execution',
            len(data)
        )

        # ==========================
        #           UPDATE
        # ==========================
    @handler_db_error
    async def update_pipeline_execution(self, pipeline_ids):

        query = text(
            '''
                UPDATE pipeline_execution
                    SET
                        status_id = :status_id
                WHERE pipeline_id = :pipeline_id
            '''
        )

        await self.session.execute(query, pipeline_ids)

        # ==========================
        #           SELECT
        # ==========================

    @handler_db_error
    async def select_pipeline_execution(
        self,
        stage_id,
        status_id,
        integration_id,
        offset,
        limit=100
    ):

        query = text(
            '''
                SELECT
                    pipeline_id,
                    order_id,
                    stage_id,
                    status_id
                FROM pipeline_execution
                WHERE stage_id = :stage_id
                    AND status_id = :status_id
                    AND integration_id = :integration_id

                LIMIT :limit
                OFFSET :offset
                ORDER BY pipeline_id
            '''
        )

        values = {
            'stage_id': stage_id,
            'status_id': status_id,
            'limit': limit,
            'offset': offset,
            'integration_id': integration_id
        }

        result = await self.session.execute(query, values)

        data = result.fetchall()

        return data
