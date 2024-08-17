from typing import Type, List
import pydantic

from app.lib import domain
from app.security import commands


class GetItems(domain.EntrypointWeb):
    route: str = "/item"
    name: str = "Get Items"
    summary: str = "Summary of get items and daissi chicken"
    description: str = "Description of get items Chicken"
    command: Type[domain.Command] | None = commands.Cks
    responses: List[domain.ExampleResponse] = [
        domain.ExampleResponse(
            status_code=200,
            description="Cuando Pollo canta",
            content={
                "trace_id": "094f1ac4-9c4f-4537-b0af-eca2c9bf3794",
                "payload": {
                    "a": 1
                },
                "errors": []
            }
        )
    ]
