from dataclasses import dataclass


@dataclass
class PipelinesExecution:
    pipeline_id: int
    order_id: int
    stage_id: int
    status_id: int
