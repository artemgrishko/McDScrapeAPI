from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db import models


async def get_all_products(
        db: AsyncSession,
        skip: int | None = None,
        limit: int | None = None,
):
    query = select(models.Product).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def get_product_by_name(db: AsyncSession, name: str):
    query = select(models.Product).filter(models.Product.name == name)
    result = await db.execute(query)
    db_product = result.scalars().first()

    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product


async def get_product_by_name_by_field(db: AsyncSession, name: str, field: str):
    query = select(models.Product).filter(models.Product.name == name)
    result = await db.execute(query)
    db_product = result.scalars().first()

    if db_product is None:
        raise HTTPException(status_code=404, detail=f"Продукт з ім'ям '{name}' не знайдено.")
    field_value = getattr(db_product, field, None)
    if field_value is None:
        raise HTTPException(status_code=404, detail=f"Поле '{field}' не існує в моделі Product.")
    return field_value
