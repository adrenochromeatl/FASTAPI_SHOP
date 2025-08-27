from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import crud, schemas, database
from ..logging_config import log
from sqlalchemy import desc

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/", response_model=schemas.Product, status_code=status.HTTP_201_CREATED)
def create_product(product: schemas.ProductCreate, db: Session = Depends(database.get_db)):
    """
    Создание нового товара.
    """
    try:
        log.info(f"Попытка создания товара: {product.name}")
        return crud.create_product(db=db, product=product)

    except Exception as e:
        log.error(f"Ошибка при создании товара {product.name}: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.get("/", response_model=List[schemas.Product])
def read_products(
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        sort: Optional[str] = None,
        db: Session = Depends(database.get_db)
):
    """
    Получение списка товаров с возможностью фильтрации по категории и сортировки.
    """
    try:
        log.info(f"Запрос списка товаров: skip={skip}, limit={limit}, category={category}, sort={sort}")

        # Базовый запрос
        query = db.query(models.Product)

        # Фильтрация по категории
        if category:
            query = query.filter(models.Product.category == category)
            log.info(f"Фильтрация товаров по категории: {category}")

        # Сортировка
        if sort == "price":
            query = query.order_by(models.Product.price)
        elif sort == "price_desc":
            query = query.order_by(desc(models.Product.price))
        elif sort == "name":
            query = query.order_by(models.Product.name)
        else:
            query = query.order_by(models.Product.id)

        products = query.offset(skip).limit(limit).all()
        log.info(f"Получено {len(products)} товаров")
        return products

    except Exception as e:
        log.error(f"Ошибка при получении списка товаров: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.get("/{product_id}", response_model=schemas.Product)
def read_product(product_id: int, db: Session = Depends(database.get_db)):
    """
    Получение товара по ID.
    """
    try:
        log.info(f"Запрос товара с ID: {product_id}")
        db_product = crud.get_product(db, product_id=product_id)
        if db_product is None:
            log.warning(f"Товар с ID {product_id} не найден")
            raise HTTPException(status_code=404, detail="Товар не найден")
        return db_product
    except Exception as e:
        log.error(f"Ошибка при получении товара {product_id}: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")