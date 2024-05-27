from sqlalchemy import Column, Integer, String, Float

from db.engine import Base


class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True)
    description = Column(String(511), nullable=True)
    calories = Column(Integer)
    fats = Column(Float)
    proteins = Column(Float)
    unsaturated_fats = Column(String(511), nullable=True)
    sugar = Column(String(511), nullable=True)
    salt = Column(String(511), nullable=True)
    portion = Column(String(511), nullable=True)
