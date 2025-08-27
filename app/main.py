from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
import os
from . import database, models, schemas, crud
from .routers import users, products, orders
from .logging_config import log
from typing import List, Optional

# Создание приложения FastAPI
app = FastAPI(
    title="Clothing Store API",
    description="Учебный пример интернет-магазина одежды на FastAPI",
    version="1.0.0"
)

# Получение абсолютного пути к директориям
base_dir = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(base_dir, "..", "templates")
static_dir = os.path.join(base_dir, "static")

# Монтирование статических файлов
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Настройка шаблонов
templates = Jinja2Templates(directory=templates_dir)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(users.router)
app.include_router(products.router)
app.include_router(orders.router)


@app.on_event("startup")
async def startup_event():
    """Событие запуска приложения"""
    log.info("Запуск приложения Clothing Store API")
    try:
        # Создание таблиц в базе данных
        database.create_tables()
        log.info("Приложение успешно запущено")
    except Exception as e:
        log.error(f"Ошибка при запуске приложения: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Событие остановки приложения"""
    log.info("Остановка приложения Clothing Store API")


# API endpoints для фронтенда
@app.get("/api/products", response_model=List[schemas.Product])
async def get_products_api(
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        sort: Optional[str] = None,
        db: Session = Depends(database.get_db)
):
    """API для получения списка товаров"""
    try:
        log.info(f"API запрос товаров: skip={skip}, limit={limit}, category={category}, sort={sort}")

        query = db.query(models.Product)

        if category:
            query = query.filter(models.Product.category == category)

        if sort == "price":
            query = query.order_by(models.Product.price)
        elif sort == "price_desc":
            query = query.order_by(desc(models.Product.price))
        elif sort == "name":
            query = query.order_by(models.Product.name)
        else:
            query = query.order_by(models.Product.id)

        products = query.offset(skip).limit(limit).all()
        return products

    except Exception as e:
        log.error(f"Ошибка при получении товаров: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера")


@app.get("/api/products/{product_id}", response_model=schemas.Product)
async def get_product_api(product_id: int, db: Session = Depends(database.get_db)):
    """API для получения товара по ID"""
    try:
        product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Товар не найден")
        return product
    except Exception as e:
        log.error(f"Ошибка при получении товара {product_id}: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера")


# Frontend routes
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Главная страница"""
    log.info("Запрос главной страницы")
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/products", response_class=HTMLResponse)
async def read_products_page(request: Request):
    """Страница товаров"""
    log.info("Запрос страницы товаров")
    return templates.TemplateResponse("products.html", {"request": request})


@app.get("/products/{product_id}", response_class=HTMLResponse)
async def read_product_detail(request: Request, product_id: int):
    """Страница деталей товара"""
    log.info(f"Запрос страницы товара ID: {product_id}")
    return templates.TemplateResponse("product-detail.html", {"request": request, "product_id": product_id})


@app.get("/cart", response_class=HTMLResponse)
async def read_cart(request: Request):
    """Страница корзины"""
    log.info("Запрос страницы корзины")
    return templates.TemplateResponse("cart.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def read_login(request: Request):
    """Страница входа"""
    log.info("Запрос страницы входа")
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def read_register(request: Request):
    """Страница регистрации"""
    log.info("Запрос страницы регистрации")
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/orders", response_class=HTMLResponse)
async def read_orders(request: Request):
    """Страница заказов"""
    log.info("Запрос страницы заказов")
    return templates.TemplateResponse("orders.html", {"request": request})


# API endpoints
@app.get("/api/health")
async def health_check():
    """Проверка здоровья приложения"""
    log.info("Запрос проверки здоровья приложения")
    return {"status": "healthy", "message": "Приложение работает нормально"}


# Заполнение базы данных тестовыми данными
@app.post("/api/seed")
async def seed_database(db: Session = Depends(database.get_db)):
    """Заполнение базы данных тестовыми данными"""
    try:
        log.info("Начало заполнения базы данных тестовыми данными")

        # Проверяем, есть ли уже пользователи
        existing_users = crud.get_users(db, limit=1)
        if existing_users:
            log.info("База данных уже заполнена")
            return {"message": "База данных уже заполнена"}

        # Создание тестового пользователя
        user_data = schemas.UserCreate(
            email="test@example.com",
            first_name="Иван",
            last_name="Иванов",
            password="password123"
        )
        user = crud.create_user(db, user_data)

        # Создание тестовых товаров
        products_data = [
            {
                "name": "Футболка хлопковая",
                "description": "Комфортная хлопковая футболка из 100% хлопка. Идеально для повседневной носки.",
                "price": 1500.0,
                "category": "Футболки",
                "size": "M",
                "color": "Белый",
                "stock_quantity": 50
            },
            {
                "name": "Джинсы классические",
                "description": "Качественные джинсы из премиального денима. Удобные и стильные.",
                "price": 3500.0,
                "category": "Джинсы",
                "size": "32",
                "color": "Синий",
                "stock_quantity": 30
            },
            {
                "name": "Куртка зимняя",
                "description": "Теплая зимняя куртка с утеплителем. Защищает от ветра и мороза.",
                "price": 8000.0,
                "category": "Куртки",
                "size": "L",
                "color": "Черный",
                "stock_quantity": 20
            },
            {
                "name": "Платье вечернее",
                "description": "Элегантное вечернее платье для особых occasions.",
                "price": 5000.0,
                "category": "Платья",
                "size": "S",
                "color": "Красный",
                "stock_quantity": 15
            },
            {
                "name": "Рубашка офисная",
                "description": "Стильная рубашка для офиса и деловых встреч.",
                "price": 2500.0,
                "category": "Рубашки",
                "size": "L",
                "color": "Голубой",
                "stock_quantity": 40
            },
            {
                "name": "Свитер шерстяной",
                "description": "Теплый свитер из натуральной шерсти для холодных дней.",
                "price": 3000.0,
                "category": "Свитеры",
                "size": "M",
                "color": "Серый",
                "stock_quantity": 25
            }
        ]

        for product_data in products_data:
            product = schemas.ProductCreate(**product_data)
            crud.create_product(db, product)

        log.info("База данных успешно заполнена тестовыми данными")
        return {"message": "База данных заполнена тестовыми данными"}

    except Exception as e:
        log.error(f"Ошибка при заполнении базы данных: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при заполнении базы данных")


# Обработчик для favicon
@app.get("/favicon.ico")
async def favicon():
    return JSONResponse(content={}, status_code=200)