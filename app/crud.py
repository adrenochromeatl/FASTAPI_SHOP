from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from . import models, schemas  # Добавим models в импорт
from .logging_config import log
from typing import List, Optional
from sqlalchemy import desc


# CRUD операции для пользователей
def get_user(db: Session, user_id: int):
    """Получение пользователя по ID"""
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if user:
            log.info(f"Пользователь с ID {user_id} найден")
        else:
            log.warning(f"Пользователь с ID {user_id} не найден")
        return user
    except SQLAlchemyError as e:
        log.error(f"Ошибка при получении пользователя {user_id}: {e}")
        raise


def get_user_by_email(db: Session, email: str):
    """Получение пользователя по email"""
    try:
        user = db.query(models.User).filter(models.User.email == email).first()
        if user:
            log.info(f"Пользователь с email {email} найден")
        else:
            log.warning(f"Пользователь с email {email} не найден")
        return user
    except SQLAlchemyError as e:
        log.error(f"Ошибка при получении пользователя по email {email}: {e}")
        raise


def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Получение списка пользователей"""
    try:
        users = db.query(models.User).offset(skip).limit(limit).all()
        log.info(f"Получено {len(users)} пользователей")
        return users
    except SQLAlchemyError as e:
        log.error(f"Ошибка при получении списка пользователей: {e}")
        raise


def create_user(db: Session, user: schemas.UserCreate):
    """Создание нового пользователя"""
    try:
        # В реальном приложении здесь должно быть хеширование пароля
        fake_hashed_password = user.password + "notreallyhashed"
        db_user = models.User(
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            hashed_password=fake_hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        log.info(f"Создан новый пользователь: {user.email}")
        return db_user
    except SQLAlchemyError as e:
        db.rollback()
        log.error(f"Ошибка при создании пользователя {user.email}: {e}")
        raise


# CRUD операции для товаров
def get_product(db: Session, product_id: int):
    """Получение товара по ID"""
    try:
        product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if product:
            log.info(f"Товар с ID {product_id} найден")
        else:
            log.warning(f"Товар с ID {product_id} не найден")
        return product
    except SQLAlchemyError as e:
        log.error(f"Ошибка при получении товара {product_id}: {e}")
        raise


def get_products(db: Session, skip: int = 0, limit: int = 100, category: Optional[str] = None):
    """Получение списка товаров с возможностью фильтрации по категории"""
    try:
        query = db.query(models.Product)
        if category:
            query = query.filter(models.Product.category == category)
            log.info(f"Фильтрация товаров по категории: {category}")

        products = query.offset(skip).limit(limit).all()
        log.info(f"Получено {len(products)} товаров")
        return products
    except SQLAlchemyError as e:
        log.error(f"Ошибка при получении списка товаров: {e}")
        raise


def create_product(db: Session, product: schemas.ProductCreate):
    """Создание нового товара"""
    try:
        db_product = models.Product(**product.dict())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        log.info(f"Создан новый товар: {product.name}")
        return db_product
    except SQLAlchemyError as e:
        db.rollback()
        log.error(f"Ошибка при создании товара {product.name}: {e}")
        raise


# CRUD операции для заказов
def create_order(db: Session, order: schemas.OrderCreate, user_id: int):
    """Создание нового заказа"""
    try:
        # Расчет общей суммы заказа
        total_amount = 0
        order_products = []

        for item in order.products:
            product = get_product(db, item.product_id)
            if not product:
                log.error(f"Товар с ID {item.product_id} не найден")
                raise ValueError(f"Товар с ID {item.product_id} не существует")

            if product.stock_quantity < item.quantity:
                log.error(f"Недостаточно товара {product.name} в наличии")
                raise ValueError(f"Недостаточно товара {product.name} в наличии")

            total_amount += product.price * item.quantity
            order_products.append(product)

            # Обновление количества товара на складе
            product.stock_quantity -= item.quantity

        # Создание заказа
        db_order = models.Order(
            user_id=user_id,
            total_amount=total_amount,
            status="pending"
        )

        # Добавление товаров к заказу
        for product in order_products:
            db_order.products.append(product)

        db.add(db_order)
        db.commit()
        db.refresh(db_order)

        log.info(f"Создан новый заказ ID {db_order.id} для пользователя ID {user_id}")
        return db_order

    except SQLAlchemyError as e:
        db.rollback()
        log.error(f"Ошибка при создании заказа: {e}")
        raise


def get_orders(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """Получение списка заказов пользователя"""
    try:
        orders = db.query(models.Order).filter(
            models.Order.user_id == user_id
        ).offset(skip).limit(limit).all()

        log.info(f"Получено {len(orders)} заказов для пользователя ID {user_id}")
        return orders
    except SQLAlchemyError as e:
        log.error(f"Ошибка при получении заказов пользователя ID {user_id}: {e}")
        raise