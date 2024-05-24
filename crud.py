from fastapi import HTTPException
from sqlalchemy.orm import Session

from db import models


def get_all_products(
        db: Session,
        skip: int | None = None,
        limit: int | None = None,
):
    return db.query(models.Product).offset(skip).limit(limit).all()


def get_product_by_name(db: Session, name: str):
    db_product = db.query(models.Product).filter(models.Product.name == name).first()

    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product


def get_product_by_name_by_field(db: Session, name: str, field: str):
    db_product = db.query(models.Product).filter(models.Product.name == name).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail=f"Продукт з ім'ям '{name}' не знайдено.")
    field_value = getattr(db_product, field, None)
    if field_value is None:
        raise HTTPException(status_code=404, detail=f"Поле '{field}' не існує в моделі Product.")
    return field_value
