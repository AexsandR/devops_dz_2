from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
import os
import datetime

# PostgreSQL из окружения
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# Явный путь для логов (без переменных окружения)
LOG_PATH = "app/logs/app.log"


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

@app.post("/users/add")
async def add_user(username: str, db: Session = Depends(get_db)):
    with open(LOG_PATH, "a") as f:
        f.write(f"get username '{username}' at {datetime.datetime.now()}\n")
    try:
        # Проверяем, что username не пустой
        if not username or not username.strip():
            raise HTTPException(status_code=400, detail="Username не может быть пустым")
        
        # Проверяем, нет ли уже пользователя с таким именем
        result = db.execute(
            text("SELECT id FROM users WHERE username = :username"), 
            {"username": username.strip()}
        )
        existing_user = result.fetchone()
        
        if existing_user:
            raise HTTPException(status_code=400, detail="Пользователь с таким именем уже существует")
        
        # Добавляем нового пользователя
        db.execute(
            text("INSERT INTO users (username) VALUES (:username)"),
            {"username": username.strip()}
        )
        db.commit()
        print("лог")
        # Логируем успешное добавление
        with open(LOG_PATH, "a") as f:
            f.write(f"add user '{username}' at {datetime.datetime.now()}\n")

        return {"status": "success", "message": f"Пользователь {username} успешно добавлен"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при добавлении пользователя: {str(e)}")