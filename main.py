from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

import crud
import schemas
from db.engine import SessionLocal

app = FastAPI()


def get_db() -> Session:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@app.get("/all_products/", response_model=list[schemas.ProductList])
def read_all_products(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 10,
):
    return crud.get_all_products(skip=skip, limit=limit, db=db)


@app.get("/products/{product_name}/", response_model=schemas.ProductList)
def read_product_by_name(product_name: str, db: Session = Depends(get_db)):
    return crud.get_product_by_name(db=db, name=product_name)


@app.get("/products/{product_name}/{product_field}/")
def read_product_by_name(
        product_name: str,
        product_field: str,
        db: Session = Depends(get_db)
):
    return crud.get_product_by_name_by_field(db=db, name=product_name, field=product_field)
