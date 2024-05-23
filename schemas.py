from pydantic import BaseModel


class ProductBase(BaseModel):
    name: str
    description: str
    calories: int
    fats: float
    proteins: float
    unsaturated_fats: str
    sugar: str
    salt: str
    portion: str


class ProductList(ProductBase):
    id: int

    class Config:
        orm_mode = True
