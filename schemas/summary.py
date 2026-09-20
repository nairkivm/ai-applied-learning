from pydantic import BaseModel

class Summary(BaseModel):
    title: str
    summary: str
    keywords: list[str]