-- Создание таблицы пользователей
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL
);

-- Вставка тестовых данных (опционально)
INSERT INTO users (username) VALUES 
    ('ivan'),
    ('maria'),
    ('alexander');

