from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, database
from ..logging_config import log

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=schemas.Order, status_code=status.HTTP_201_CREATED)
def create_order(order: schemas.OrderCreate, user_id: int = 1, db: Session = Depends(database.get_db)):
    """
    Создание нового заказа.

    - **user_id**: ID пользователя (в учебных целях фиксированный)
    - **products**: Список товаров в заказе с количеством
    """
    try:
        log.info(f"Попытка создания заказа для пользователя ID: {user_id}")
        return crud.create_order(db=db, order=order, user_id=user_id)

    except ValueError as e:
        log.warning(f"Ошибка валидации при создании заказа: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        log.error(f"Ошибка при создании заказа: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.get("/", response_model=List[schemas.Order])
def read_orders(
        user_id: int = 1,
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(database.get_db)
):
    """
    Получение списка заказов пользователя.

    - **user_id**: ID пользователя (в учебных целях фиксированный)
    - **skip**: Количество пропускаемых записей
    - **limit**: Максимальное количество возвращаемых записей
    """
    try:
        log.info(f"Запрос списка заказов для пользователя ID: {user_id}")
        orders = crud.get_orders(db, user_id=user_id, skip=skip, limit=limit)
        return orders
    except Exception as e:
        log.error(f"Ошибка при получении списка заказов: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.get("/{order_id}", response_model=schemas.Order)
def read_order(order_id: int, db: Session = Depends(database.get_db)):
    """
    Получение заказа по ID.

    - **order_id**: ID заказа
    """
    try:
        log.info(f"Запрос заказа с ID: {order_id}")
        # В реальном приложении здесь должна быть проверка прав доступа
        order = db.query(schemas.Order).filter(schemas.Order.id == order_id).first()
        if order is None:
            log.warning(f"Заказ с ID {order_id} не найден")
            raise HTTPException(status_code=404, detail="Заказ не найден")
        return order
    except Exception as e:
        log.error(f"Ошибка при получении заказа {order_id}: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")