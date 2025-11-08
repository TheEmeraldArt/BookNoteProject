from fastapi import FastAPI, Depends, Response, HTTPException

from endpoints.books_routers import router as books_router

from endpoints.users_routers import router as users_router

import time

from datetime import datetime

from loguru import logger

from database import UserModel 

from auth.authentication import require_admin

from session.session_db import init_db  

from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Gauge, Histogram

from sqlalchemy import text

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from typing import Annotated

import psutil



# Конфигурация
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"

# Настройка логгирования с помощью библиотеки loguru
logger.add(
    "app.log",
    rotation="10 MB",
    retention="30 days",
    level="INFO",
    backtrace=True,
    diagnose=True
)

# Инициализация базы данных
engine = create_async_engine(DATABASE_URL, echo=True)
new_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():
    """Зависимость для получения сессии БД"""
    async with new_session() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            raise HTTPException(status_code=500, detail="Database connection error")

SessionDep = Annotated[AsyncSession, Depends(get_session)]


# Создание метрик

# Технические метрики 
REQUEST_COUNT = Counter(
    'http_requests_total', 
    'Total HTTP Requests', 
    ['method', 'endpoint', 'status_code']
)


REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)


# Системные метрики
CPU_USAGE = Gauge('cpu_usage_percent', 'CPU usage percentage')
MEMORY_USAGE = Gauge('memory_usage_mb', 'Memory usage in MB')
DISK_USAGE = Gauge('disk_usage_percent', 'Disk usage percentage')


# Бизнес-метрики
DATABASE_SIZE = Gauge('database_size_mb', 'Database size in MB')
BOOKS_COUNT = Gauge('books_count', 'Total number of books in database')
USERS_COUNT = Gauge('users_count', 'Total number of registered users')
ACTIVE_CONNECTIONS = Gauge('postgres_active_connections', 'Number of active database connections')


# Создание FastAPI приложения
app = FastAPI(
    title="Book Note API",
    description="API для управления книгами и пользователями с мониторингом",
    
)


# Подлючения роутеров 
app.include_router(books_router) # ednpoinds для книг
app.include_router(users_router) # ednpoinds для пользователей


# Функции для метрик
def update_system_metrics():
    """Обновление системных метрик с обработкой ошибок"""
    try:
        logger.debug("Updating system metrics...")
        # CPU метрика
        cpu_percent = psutil.cpu_percent(interval=1)
        CPU_USAGE.set(cpu_percent)
        
        # Memory метрика
        memory = psutil.virtual_memory()
        memory_used_mb = memory.used / 1024 / 1024
        MEMORY_USAGE.set(memory_used_mb)
        
        # Disk метрика
        disk = psutil.disk_usage('/')
        DISK_USAGE.set(disk.percent)
        logger.debug("Database metrics updated successfully")
        logger.debug(f"System metrics updated - CPU: {cpu_percent}%, Memory: {memory_used_mb:.2f}MB")
       
    except Exception as e:
        logger.error(f"Error updating system metrics: {e}")


async def update_database_metrics(session: AsyncSession):
    """Обновление метрик базы данных с обработкой ошибок"""
    try:
        logger.debug("Updating database metrics...")
        
        # Размер базы данных
        size_result = await session.execute(text("SELECT pg_database_size(current_database())"))
        db_size_bytes = size_result.scalar()
        if db_size_bytes:
            DATABASE_SIZE.set(db_size_bytes / 1024 / 1024)
        
        # Количество книг
        books_result = await session.execute(text("SELECT COUNT(*) FROM books"))
        books_count = books_result.scalar()
        if books_count is not None:
            BOOKS_COUNT.set(books_count)
        
        # Количество пользователей
        users_result = await session.execute(text("SELECT COUNT(*) FROM users"))
        users_count = users_result.scalar()
        if users_count is not None:
            USERS_COUNT.set(users_count)
        
        # Активные подключения
        connections_result = await session.execute(text("""
            SELECT count(*) FROM pg_stat_activity 
            WHERE state = 'active' AND datname = current_database()
        """))
        active_conn = connections_result.scalar()
        if active_conn is not None:
            ACTIVE_CONNECTIONS.set(active_conn)
        
        logger.debug("Database metrics updated successfully")
        
    except Exception as e:
        logger.error(f"Error updating database metrics: {e}")
        

# Middleware - это помошник который считает сколько времени он занял, считает сколько всего запросов пришло, записывает это в Prometheus метрики
@app.middleware("http")
async def collect_request_metrics(request, call_next):
    """Middleware для сбора метрик HTTP запросов"""
    start_time = time.time()
    method = request.method
    endpoint = request.url.path
    
    try:
        response = await call_next(request)
        status_code = response.status_code
        
        # Записываем метрики только после успешного выполнения
        duration = time.time() - start_time
        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
        
        logger.debug(f"Request {method} {endpoint} - {status_code} - {duration:.3f}s")
        
        return response
        
    except Exception as e:
        # Метрики для ошибок
        duration = time.time() - start_time
        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=500).inc()
        
        logger.error(f"Request {method} {endpoint} failed: {e}")
        raise e


# Ивенты запуска и завершиния работы приложения
@app.on_event("startup")
async def on_startup():
    """Инициализация при запуске приложения"""
    logger.info("Запуск приложения...")
    try:
        await init_db()
        logger.info("Таблицы базы данных созданы/проверены")
    except Exception as e:
        logger.error(f" Ошибка инициализации БД: {e}")
        raise

@app.on_event("shutdown")
async def on_shutdown():
    """Очистка при завершении приложения"""
    logger.info("Завершение работы приложения...")


# Эндпоинты 
@app.get("/", tags=["ROOT 🏠"], summary="Корневой эндпоинт")
async def root():
    """Корневой эндпоинт приложения"""
    return {
        "message": "📚 Добро пожаловать в Book Note API!",
    }


@app.get("/health", tags=["HEALTH CHECK 💊"], summary="Проверка работы приложения")
async def health_check(current_user: UserModel = Depends(require_admin)):
    """Проверка здоровья приложения и аутентификации"""
    return {
        "status": "200",
        "message": "Все системы работают нормально",
        "timestamp": datetime.now().isoformat(),
        "user": current_user.username
    }


@app.get("/metrics", tags=["PROMETHEUS METRICS 📊"], summary="Метрики приложения")
async def metrics_endpoint(session: SessionDep):
    """
    Эндпоинт для Prometheus метрик
    Возвращает:
    - Системные метрики (CPU, память, диск)
    - Метрики базы данных (размер, подключения)
    - Бизнес-метрики (книги, пользователи)
    - Метрики HTTP запросов
    """
    try:
        # Обновляем все метрики
        update_system_metrics()
        await update_database_metrics(session)
        
        # Генерируем и возвращаем метрики
        return Response(
            generate_latest(),
            media_type=CONTENT_TYPE_LATEST
        )
        
    except Exception as e:
        logger.error(f"Error in metrics endpoint: {e}")
        raise HTTPException(status_code=500, detail="Metrics generation error")


@app.get("/test-db", tags=["DATABASE TEST 💾"], summary="Проверка работы базы данных")
async def test_db(session: SessionDep, current_user: UserModel = Depends(require_admin)):
    """Тестовый эндпоинт для проверки подключения к базе данных"""
    try:
        # Проверяем подключение к БД
        db_result = await session.execute(text("SELECT current_database(), version()"))
        db_info = db_result.fetchone()
        
        # Получаем статистику
        books_result = await session.execute(text("SELECT COUNT(*) FROM books"))
        books_count = books_result.scalar()
        
        users_result = await session.execute(text("SELECT COUNT(*) FROM users"))
        users_count = users_result.scalar()
        
        return {
            "status": "success",
            "database": {
                "name": db_info[0],
                "version": db_info[1].split()[1] if db_info[1] else "unknown"
            },
            "statistics": {
                "books_count": books_count,
                "users_count": users_count
            },
            "user": current_user.username,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Database test failed: {e}")
        return {
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }