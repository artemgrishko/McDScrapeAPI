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
def read_all_products(db: Session = Depends(get_db)):
    return crud.get_all_products(db)
