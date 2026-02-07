from app.db.models import User, Task
from datetime import datetime


async def add_users(db):
    users = [
        User(
            id=1,
            name="Скотт Майкл Георгиевич",
            hashed_password="$2b$12$7Z6RAKy5guMxCI1SZ6TnPe3nc7YA9MZwNpKIye3II5mhv2RI..jsq",
            position="CEO",
            is_superuser=True,
            is_verified=True,
            email="dundermifflin@example.com",
            phone="89777907157",
        ),
        User(
            id=2,
            name="Паркер Питер Бенджами",
            hashed_password="$2b$12$7Z6RAKy5guMxCI1SZ6TnPe3nc7YA9MZwNpKIye3II5mhv2RI..jsq",
            position="Backend-разработчик",
            is_superuser=False,
            is_verified=True,
            email="p.parker@example.com",
            phone="89100000102",
        ),
        User(
            id=3,
            name="Бриджертон Бенедикт Эдмундович",
            hashed_password="$2b$12$7Z6RAKy5guMxCI1SZ6TnPe3nc7YA9MZwNpKIye3II5mhv2RI..jsq",
            position="UI-дизайнер",
            is_superuser=False,
            is_verified=True,
            email="benbridgerton@example.com",
            phone="89159987867",
        ),
    ]
    db.add_all(users)
    await db.flush()


async def add_tasks(db):
    tasks = [
        Task(
            id=53,
            title="Background Jobs: Processing User-Generated Content",
            content="Реализовать систему фоновой обработки загружаемых пользователями изображений и видео. Сервис должен: 1) принимать файл, 2) помещать задачу в очередь (Redis), 3) обрабатывать (сжатие, создание превью, извлечение метаданных) воркером, 4) обновлять статус в БД, 5) иметь эндпоинт для проверки статуса обработки. Обеспечить отказоустойчивость и логирование.",
            importance_level="C",
            created_at=datetime.strptime(
                "2026-01-27 10:23:21.401096", "%Y-%m-%d %H:%M:%S.%f"
            ),
            updated_at=datetime.strptime(
                "2026-01-28 15:57:49.399463", "%Y-%m-%d %H:%M:%S.%f"
            ),
            completed_at=None,
            user_id=2,
            deadline_date=datetime.strptime("2026-01-31 19:00:00", "%Y-%m-%d %H:%M:%S"),
        ),
        Task(
            id=40,
            title="Дизайн-аудит и концепт лендинга для новой фичи «Умный инвойс»",
            content="Нужен срочный дизайн-аудит текущего интерфейса генератора счетов и быстрый концепт лендинга для новой фичи «Умный инвойс». Сделать скриншоты с пометками боли и прототип главного экрана лендинга в Figma за 3 дня.",
            importance_level="A",
            remark="Не забудь про мобилки и бренд-цвета. Текст в макете должен оставаться текстом.",
            created_at=datetime.strptime(
                "2026-01-29 11:40:21.401096", "%Y-%m-%d %H:%M:%S.%f"
            ),
            updated_at=datetime.strptime(
                "2026-01-29 18:49:49.399463", "%Y-%m-%d %H:%M:%S.%f"
            ),
            completed_at=datetime.strptime(
                "2026-01-29 18:49:49.407422", "%Y-%m-%d %H:%M:%S.%f"
            ),
            user_id=3,
            deadline_date=datetime.strptime("2026-01-29 19:00:00", "%Y-%m-%d %H:%M:%S"),
        ),
    ]

    db.add_all(tasks)
    await db.flush()
