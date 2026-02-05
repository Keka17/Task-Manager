# Real-Time Task Manager с интеграцией WebSocket <img width="90" height="84" alt="images (1)-Photoroom (1)" src="https://github.com/user-attachments/assets/2b070f18-4052-42c6-9aca-18076b42c685" />
Диспетчер задач в реальном времени, построенный на FastAPI. Проект включает продвинутую систему аутентификации (JWT), фоновые задачи через Celery, 
уведомления на почту через SMTP-сервер и поддержку WebSocket для обновления доски с задачами в реальном времени. 


## Основной функционал
* Регистрация и аутентификация OAuth2 для доступа к функционалу приложения.
* СRUD-операции для работы с задачами.
* Асинхронное взаимодействие с PostgreSQL.
* Обновление статуса задач в режиме реального времени с использованием WebSocket.

## Стек технологий
* Backend: _FastAPI, Uvicorn, Pydantic v2_
* Database: _PostgreSQL, SQLAlchemy, Alembic_
* Broker: _Redis_
* Tasks: _Celery, Celery Beat_
* Security: _JWT (PyJWT), Passlib (bcrypt), Cryptography_
* External services: _HTTPX, Requests, FastAPI-Mail_
* Templates: _Jinja2_
* Logging: _Loguru_
* Testing: _Pytest, Pytest-Asyncio_
* DevOps: _Docker, Docker Compose_


## Структура проекта
```bash
.FastAPI_Project
├── app
│   ├── api
│   │   ├── __init__.py
│   │   ├── endpoints/
│   │   ├── schemas/
│   │   └── websocket_board.py
│   ├── core/
│   ├── db
│   │   ├── __init__.py
│   │   ├── alembic/
│   │   ├── database.py
│   │   └── models.py
│   ├── dependencies/
│   ├── exceptions/
│   ├── handlers/
│   ├── main.py
│   ├── __init__.py
│   ├── middlewares/
│   ├── services/
│   ├── static
│   │   ├── pictures/
│   │   ├── scripts/
│   │   └── styles/
│   ├── tasks/
│   ├── templates/
│   └── utils/ 
├── logs/
├── tests/
├── .dockerignore
├── .gitignore
├── .env
├── .env.docker
├── alembic.ini
├── docker-compose.yaml
├── Dockerfile
├── pytest.ini
├── requirements.txt

```
### Директории и файлы
* `app`: Верхний уровень, содержит основной код приложения.
    * `api`: Содержит API-эндпоинты для пользователей, аутентификации, задач и WebSocket-соединений, Pydantic-схемы для валидации и сериализации данных.
    * `core`: Cодержит общие настройки конфигурации, безопасности (JWT), менеджер активных WebSocket-соединений.
    * `db`: Файлы миграций Alembic, конфигурация асинхронного подключения к базе данных, классы моделей SqlAlchemy.
    * `dependencies`: Зависимости (Dependencies) для проверки JWT-токенов и прав доступа путем извлечения текущего пользователя из HTTP-запросов и WebSocket-соединений.
    * `exceptions`: Классы кастомных user-friendly исключений.
    * `handlers`: Перехват ошибок (например, 404, 500) и возврат структурированных JSON-ответов.
    * `main.py`: Корень проекта для запуска FastAPI-приложения.
    * `middlewares`: Промежуточное ПО для логирования запрсов и ответов.
    * `services`: Бизнес-логика приложения: CRUD-операции, взаимодействие с БД.
    * `static`: Cтатические файлы (изображения, js-скрипты, css-классы).
    * `tasks`: Конфигурация Celery для выполнения фоновых задач и управления расписанием периодических событий Celery Beat.
    * `templates`: HTML-шаблоны для писем, страницы входа и доски с задачами.
    * `utils`: Файл конфигурации и логики для асинхронной отправки email-уведомлений.
* `logs`: Файлы с логами разных уровней (INFO, WARNING, ERROR).
* `tests`: Тесты эндпоинтов, фикстуры и вспомогательные функции.
* `.dockerignore`: Список файлов и директорий, игнорируемых при сборке Docker-контейнера.
* `.gitignore`: Список файлов и директорий, игнорируемых системой контроля версий.
* `.env`: Хранение конфиденциальной информации (напр.,пароли баз данных, почты).
* `env.docker`: Хранение переменных окружения для Docker-контейнеризации.
* `alembic.ini`: Конфигурационный файл инструмента миграции баз данных Alembic.
* `docker-compose.yaml`: Файл Docker Compose, содержащий инструкции, необходимые для запуска и настройки сервисов.
* `Dockerfile`: Набор инструкций для автоматической сборки образа Docker.
* `pytest.ini`: Конфигурационный файл для pytest.
* `requirements.txt`: Список зависимостей проекта.

## Установка и запуск
### Локальный запуск
   * __Требования__: перед запуском приложения убедитесь, что у вас установлены следующие компоненты:
      * Python 3.10+
      * PostgreSQL
      * Redis

   1. __Клонирование репозитория__
      ```bash
       git clone https://github.com/Keka17/Task-Manager

       cd Task-Manager
      ```
   
2. __Создание и активация виртуальной среды__
   
   ```bash
      python3 -m venv venv

      venv\Scripts\activate (Windows)

      source venv/bin/activate (MacOS, Linux)
   ```
  
3. __Установка зависимостей__
   
    ```bash
      pip install -r requirements.txt
    ```
4. __Настройка переменных окружения__
   
Cоздайте файл `.env` в корне проекта, заполнив его в соответствии с файлом `.env.example`. Параметры `COMPANY_DOMAIN`, `POSITIONS` _необязательны_.

5. __Запуск приложения__
   
   Для полноценной работы нужно запустить три компонента:
     * __API сервер__: из корневой папки
    
    ```bash
    uvicorn app.main:app --reload
    ```
     * __Celery Worker__:
    
    ```bash
    celery -A app.tasks.celery_app.celery_app worker --loglevel=info
    ```
     * __Celery Beat__:
    
    ```bash
    celery -A app.tasks.celery_app.celery_app beat --loglevel=info
    ```

### Запуск через Docker

__Примечание__: этот способ запуска __быстрее__, т.к. не требует отдельной установки PostgreSQL и Redis.

1. __Настройка переменных окружения__
   
Cоздайте файл `.env.docker` в корне проекта, заполнив его в соответствии с файлом `.env.example`. Параметры `COMPANY_DOMAIN`, `POSITIONS` _необязательны_.

2. __Сборка и запуск__

   Убедитесь, что у вас установлен __Docker__ и __Docker Compose__, затем выполните:
   
   ```bash
    docker-compose --env-file .env.docker up --build
    ```


### Доступ к приложению
* После успешного запуска API будет доступно по адресу: http://localhost:8000/.
* Доска с задачми доступна по адресу http://localhost:8000/ws/enter. Неавторизованного пользователя отправят на страницу входа.
* После запуска сервера доступна интерактивная документация с возможностью проверить функционал:
   * __Swagger__: http://localhost:8000/docs
   * __Redoc__: http://localhost:8000/redoc

## Эндпоинты
* ### __Users__
  * `POST /users/signup/`: Регистрация нового пользователя
  * `GET /users/`: Получение списка всех пользователей (protected), доступно только администратору (поле `is_superuser` в БД).
  * `GET /users/{user_id}/`: Получение информации о конкретном пользователе (protected), доступно только администратору (поле `is_superuser` в БД).
  * `DELETE /users/{user_id}/`: Удаление конкретного пользователя (protected), доступно только администратору (поле `is_superuser` в БД).

* ### __Auth__
   * `POST /auth/login/`: Аутентификация для получения пары токенов.
   * `POST /auth/refresh/`: Обновление пары токенов. В заголовках обязательно указывать refresh-token ('x-refresh-token`).
   * `POST /auth/logout/`: Выход из системы. В заголовках обязательно указывать refresh-token ('x-refresh-token`).
   * `GET /auth/login-page`: Отображение HTML-страницы входа.
     
* ### __Tasks__
  * `POST /tasks/`: Создание новой задачи (protected).
  * `GET /tasks/`: Получения списка всех задач (protected). Возможные параметры запроса: level, completed.
  * `GET /tasks/{task_id}/`: Получение конкретной задачи (protected).
  * `GET /tasks/my_task`: Получения списка задач пользователя (protected). Информация о пользователе достается из токена.
  * `PATCH /tasks/{task_id}/`: Обновление поля `content`. Действие доступно только автору задачи (protected).
  * `PATCH /tasks/complete/{task_id}`: Завершение задачи путем добавления временной метки в поле `completed_at`. Эндпоинт оступен только автору задачи (protected).
  * `PATCH /tasks/remark/{task_id}`: Добавление ремарки к задаче (protected). Действие доступно только администратору.
  * `DELETE /tasks/{task_id}/`: Удаление конкретной задачи (protected). Действие доступно только автору задачи и администратору.
  * `GET /tasks/board/`: Получение списка всех незавершенных задач для доски. Использутеся на фронтенде.
  * `GET /tasks/board/{task_id}`: Получение конкретной задачи. Использутеся на фронтенде.
