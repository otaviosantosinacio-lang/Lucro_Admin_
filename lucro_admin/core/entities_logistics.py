from dataclasses import dataclass


@dataclass
class RegisterLogistic():
    external_service_id: int
    service_name: str
    logistics_name: str
    status: bool
