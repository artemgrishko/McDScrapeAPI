from pydantic import BaseModel


class ProductBase(BaseModel):
    name: str
    description: str
    calories: int | None
    fats: float | None
    proteins: float | None
    unsaturated_fats: str
    sugar: str
    salt: str
    portion: str


class ProductList(ProductBase):
    id: int

    class Config:
        orm_mode = True
