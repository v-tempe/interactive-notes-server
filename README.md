# Interactive Notes API (Backend)

Серверная часть приложения "Сервис для создания интерактивных конспектов". Реализована на Django REST Framework с использованием PostgreSQL и JWT-аутентификации.

## Стек технологий
- **Python 3.10+**
- **Django 4.x / DRF**
- **PostgreSQL**
- **Docker & Docker Compose**
- **SimpleJWT** для аутентификации

## Структура проекта
- `interactive_notes/` — настройки проекта и конфигурация.
- `notes/` — основное приложение (конспекты, разделы, блоки, соавторы).
- `users/` — приложение для управления пользователями и регистрацией.

## Тестирование
- `users/tests` - проверка регистрации и аутентификации
- `notes/tests` - фаззинг-тестирование, а также проверка RBAC и валидации

## Локальный запуск

1. Клонируйте репозиторий себе на компьютер:
   - HTTPS
      ```bash
      https://github.com/v-tempe/interactive-notes-server.git
      ```
   - SSH
       ```bash
       git clone git@github.com:v-tempe/interactive-notes-server.git
       ```
   - GitHub CLI
       ```bash
       gh repo clone v-tempe/interactive-notes-server
       ```
2. Скопируйте `.env.example` в `.env` и заполните переменные окружения.
2. Соберите и запустите контейнеры:
   ```bash
   docker compose up --build
   ```
   
## Демонстрация
Проект развёрнут в облачной системе Render.  
Корневой URL: https://interactive-notes-server.onrender.com/

## Документация
Swagger: https://interactive-notes-server.onrender.com/api/docs  
ReDoc: https://interactive-notes-server.onrender.com/api/redoc  
Скачать YML-файл: https://interactive-notes-server.onrender.com/api/schema  
