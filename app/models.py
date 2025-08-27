from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
from .logging_config import log

# Ассоциативная таблица для связи многие-ко-многим между заказами и товарами
order_product_association = Table(
    'order_product',
    Base.metadata,
    Column('order_id', Integer, ForeignKey('orders.id')),
    Column('product_id', Integer, ForeignKey('products.id')),
    Column('quantity', Integer, nullable=False, default=1)
)


class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связь с заказами
    orders = relationship("Order", back_populates="user")

    def __repr__(self):
        return f"<User {self.email}>"


class Product(Base):
    """Модель товара"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    category = Column(String, index=True, nullable=False)
    size = Column(String, nullable=False)
    color = Column(String, nullable=False)
    stock_quantity = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связь с заказами
    orders = relationship("Order", secondary=order_product_association, back_populates="products")

    def __repr__(self):
        return f"<Product {self.name}>"


class Order(Base):
    """Модель заказа"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(String, default="pending")  # pending, confirmed, shipped, delivered, cancelled
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Связи
    user = relationship("User", back_populates="orders")
    products = relationship("Product", secondary=order_product_association, back_populates="orders")

    def __repr__(self):
        return f"<Order {self.id} - {self.status}>"