from app.db.models import User


async def add_users(db):
    users = [
        User(
            name="Скотт Майкл Георгиевич",
            hashed_password="$2b$12$7Z6RAKy5guMxCI1SZ6TnPe3nc7YA9MZwNpKIye3II5mhv2RI..jsq",
            position="CEO",
            is_superuser=True,
            email="dundermifflin@example.com",
            phone="89777907157",
        ),
        User(
            name="Паркер Питер Бенджами",
            hashed_password="$2b$12$7Z6RAKy5guMxCI1SZ6TnPe3nc7YA9MZwNpKIye3II5mhv2RI..jsq",
            position="SMM-специалист",
            is_superuser=False,
            email="p.parker@example.com",
            phone="89100000102",
        ),
        User(
            name="Бриджертон Бенедикт Эдмундович",
            hashed_password="$2b$12$7Z6RAKy5guMxCI1SZ6TnPe3nc7YA9MZwNpKIye3II5mhv2RI..jsq",
            position="UI-дизайнер",
            is_superuser=False,
            email="benbridgerton@example.com",
            phone="89159987867",
        ),
    ]
    db.add_all(users)
    await db.flush()
