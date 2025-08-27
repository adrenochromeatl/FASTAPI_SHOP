from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, database
from ..logging_config import log

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    """
    Создание нового пользователя.

    - **email**: Email пользователя (должен быть уникальным)
    - **first_name**: Имя пользователя
    - **last_name**: Фамилия пользователя
    - **password**: Пароль (минимум 6 символов)
    """
    try:
        log.info(f"Попытка создания пользователя: {user.email}")

        # Проверка существования пользователя
        db_user = crud.get_user_by_email(db, email=user.email)
        if db_user:
            log.warning(f"Пользователь с email {user.email} уже существует")
            raise HTTPException(
                status_code=400,
                detail="Пользователь с таким email уже зарегистрирован"
            )

        return crud.create_user(db=db, user=user)

    except Exception as e:
        log.error(f"Ошибка при создании пользователя {user.email}: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.get("/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    """
    Получение списка пользователей.

    - **skip**: Количество пропускаемых записей
    - **limit**: Максимальное количество возвращаемых записей
    """
    try:
        log.info(f"Запрос списка пользователей: skip={skip}, limit={limit}")
        users = crud.get_users(db, skip=skip, limit=limit)
        return users
    except Exception as e:
        log.error(f"Ошибка при получении списка пользователей: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.get("/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(database.get_db)):
    """
    Получение пользователя по ID.

    - **user_id**: ID пользователя
    """
    try:
        log.info(f"Запрос пользователя с ID: {user_id}")
        db_user = crud.get_user(db, user_id=user_id)
        if db_user is None:
            log.warning(f"Пользователь с ID {user_id} не найден")
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        return db_user
    except Exception as e:
        log.error(f"Ошибка при получении пользователя {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")