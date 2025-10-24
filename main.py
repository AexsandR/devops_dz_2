from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
import os

# Используем localhost для подключения к PostgreSQL в Docker
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://qwe:12345@localhost:5432/users")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI(title="Users API", version="1.0.0")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def test():
    return {"database_url": DATABASE_URL, "message": "API работает!"}

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

@app.get("/users", response_model=list[dict])
async def get_all_users(db: Session = Depends(get_db)):
    try:
        # Выполняем сырой SQL запрос
        result = db.execute(text("SELECT id, username FROM users ORDER BY id"))
        users = result.fetchall()
        
        # Преобразуем результат в словари
        return [{"id": user.id, "username": user.username} for user in users]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка подключения к БД: {str(e)}")

@app.post("/init-db")
async def initialize_database(db: Session = Depends(get_db)):
    """Создает таблицу и тестовые данные"""
    try:
        # Создаем таблицу
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Добавляем тестовые данные
        db.execute(text("""
            INSERT INTO users (username, email) VALUES 
            ('alice', 'alice@example.com'),
            ('bob', 'bob@example.com'),
            ('charlie', 'charlie@example.com')
            ON CONFLICT (username) DO NOTHING
        """))
        
        db.commit()
        return {"message": "База данных инициализирована успешно"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка инициализации БД: {str(e)}")