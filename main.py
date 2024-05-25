import crud
import schemas

from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from dependencies import get_db

app = FastAPI()


@app.get("/all_products/", response_model=List[schemas.ProductList])
async def read_all_products(
        db: AsyncSession = Depends(get_db),
        skip: int = 0,
        limit: int = 10,
):
    return await crud.get_all_products(skip=skip, limit=limit, db=db)


@app.get("/products/{product_name}/", response_model=schemas.ProductList)
async def read_product_by_name(product_name: str, db: AsyncSession = Depends(get_db)):
    return await crud.get_product_by_name(db=db, name=product_name)


@app.get("/products/{product_name}/{product_field}/")
async def read_product_by_name_and_field(
        product_name: str,
        product_field: str,
        db: AsyncSession = Depends(get_db)
):
    return await crud.get_product_by_name_by_field(db=db, name=product_name, field=product_field)
