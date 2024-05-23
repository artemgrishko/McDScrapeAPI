from sqlalchemy.orm import Session

from db import models


def get_all_products(db: Session):
    return db.query(models.Product).all()
