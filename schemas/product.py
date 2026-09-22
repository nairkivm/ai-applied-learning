from pydantic import BaseModel


class Product(BaseModel):
    name: str
    category: str
    price: float
    description: str
