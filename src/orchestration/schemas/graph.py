from pydantic import BaseModel, Field

class LinkedStandard(BaseModel):
    standard_number: str
    title: str | None = None
    relationship: str

class GraphDetails(BaseModel):
    found: bool
    standard_number: str
    title: str | None = None
    linked_standards: list[LinkedStandard] = Field(default_factory=list)

class GraphResponse(BaseModel):
    graph: GraphDetails