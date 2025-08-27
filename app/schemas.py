from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime


# Базовые схемы
class UserBase(BaseModel):
    """Базовая схема пользователя"""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)


class UserCreate(UserBase):
    """Схема для создания пользователя"""
    password: str = Field(..., min_length=6)


class User(UserBase):
    """Схема пользователя для ответа"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    """Базовая схема товара"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    category: str
    size: str
    color: str
    stock_quantity: int = Field(..., ge=0)


class ProductCreate(ProductBase):
    """Схема для создания товара"""
    pass


class Product(ProductBase):
    """Схема товара для ответа"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class OrderProduct(BaseModel):
    """Схема товара в заказе"""
    product_id: int
    quantity: int = Field(..., ge=1)


class OrderBase(BaseModel):
    """Базовая схема заказа"""
    products: List[OrderProduct]


class OrderCreate(OrderBase):
    """Схема для создания заказа"""
    pass


class Order(OrderBase):
    """Схема заказа для ответа"""
    id: int
    user_id: int
    total_amount: float
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Схемы для аутентификации
class Token(BaseModel):
    """Схема токена"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Схема данных токена"""
    email: Optional[str] = None