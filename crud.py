from fastapi import HTTPException
from sqlalchemy.orm import Session

from db import models


def get_all_products(db: Session):
    return db.query(models.Product).all()


def get_product_by_name(db: Session, name: str):
    db_product = db.query(models.Product).filter(models.Product.name == name).first()

    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product
