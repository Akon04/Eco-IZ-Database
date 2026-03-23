from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.admin import EcoCategory, Habit
from app.models.challenge import Challenge, UserChallenge
from app.models.chat import ChatMessage
from app.models.post import Post
from app.models.user import Activity, User
from app.services.auth import hash_password


def ensure_seed_data(db: Session) -> None:
    existing = db.scalar(select(User).where(User.email == "user@ecoiz.app"))
    if not existing:
        user = User(
            full_name="Пользователь",
            email="user@ecoiz.app",
            username="user",
            password_hash=hash_password("password123"),
            role="USER",
            status="ACTIVE",
            is_email_verified=True,
            points=90,
            streak_days=2,
            co2_saved_total=8.6,
        )
        db.add(user)
        db.flush()
    else:
        user = existing

    admin = db.scalar(select(User).where(User.email == "admin@ecoiz.app"))
    if not admin:
        admin = User(
            full_name="Администратор",
            email="admin@ecoiz.app",
            username="admin",
            password_hash=hash_password("admin123"),
            role="ADMIN",
            status="ACTIVE",
            is_email_verified=True,
            points=0,
            streak_days=0,
            co2_saved_total=0,
        )
        db.add(admin)
        db.flush()

    challenge_specs = [
        ("7 эко-действий за неделю", "Добавь 7 любых экологичных активностей", 7, 60, "leaf.fill", 0x43B244, 0xEAF8DF),
        ("3 дня без пластика", "Отмечай действия категории Пластик", 3, 40, "waterbottle.fill", 0x1AA5E6, 0xE7F5FF),
        ("Эко-транспорт", "5 поездок пешком/велосипедом/метро", 5, 45, "figure.walk.circle.fill", 0xF09A00, 0xFFF5E2),
    ]
    challenges: list[Challenge] = []
    for title, description, target_count, reward_points, badge_symbol, badge_tint_hex, badge_background_hex in challenge_specs:
        challenge = db.scalar(select(Challenge).where(Challenge.title == title))
        if not challenge:
            challenge = Challenge(
                title=title,
                description=description,
                target_count=target_count,
                reward_points=reward_points,
                badge_symbol=badge_symbol,
                badge_tint_hex=badge_tint_hex,
                badge_background_hex=badge_background_hex,
            )
            db.add(challenge)
            db.flush()
        challenges.append(challenge)

    categories: list[EcoCategory] = []
    for name, description, color, icon in [
        ("Энергия", "Привычки для экономии электричества и тепла", "#F09A00", "bolt"),
        ("Вода", "Привычки для бережного использования воды", "#1AA5E6", "drop"),
        ("Пластик", "Сокращение одноразового пластика", "#43B244", "leaf"),
    ]:
        category = db.scalar(select(EcoCategory).where(EcoCategory.name == name))
        if not category:
            category = EcoCategory(name=name, description=description, color=color, icon=icon)
            db.add(category)
            db.flush()
        categories.append(category)

    for title, description, points, co2_value, water_value, energy_value, category in [
        ("Выключать лишний свет", "Отключай свет при выходе из комнаты", 10, 0.3, 0, 0.5, categories[0]),
        ("Короткий душ", "Сократи время душа до пяти минут", 12, 0.2, 8, 0.2, categories[1]),
        ("Многоразовая бутылка", "Используй свою бутылку вместо одноразовой", 9, 0.1, 0, 0, categories[2]),
    ]:
        if not db.scalar(select(Habit).where(Habit.title == title)):
            db.add(
                Habit(
                    title=title,
                    description=description,
                    points=points,
                    co2_value=co2_value,
                    water_value=water_value,
                    energy_value=energy_value,
                    category_id=category.id,
                )
            )

    if not db.scalar(select(UserChallenge).where(UserChallenge.user_id == user.id)):
        db.add_all(
            [
                UserChallenge(user_id=user.id, challenge_id=challenges[0].id, current_count=2, is_completed=False),
                UserChallenge(user_id=user.id, challenge_id=challenges[1].id, current_count=1, is_completed=False),
                UserChallenge(user_id=user.id, challenge_id=challenges[2].id, current_count=0, is_completed=False),
            ]
        )

    now = datetime.now(timezone.utc)
    if not db.scalar(select(Activity).where(Activity.user_id == user.id)):
        db.add_all(
            [
                Activity(user_id=user.id, category="Энергия", title="Отключил ненужные приборы", co2_saved=0.5, points=10, created_at=now - timedelta(hours=20)),
                Activity(user_id=user.id, category="Пластик", title="Многоразовая сумка", co2_saved=0.5, points=10, created_at=now - timedelta(hours=44)),
            ]
        )
    if not db.scalar(select(Post).where(Post.user_id == user.id)):
        db.add_all(
            [
                Post(user_id=user.id, author_name="Нурс", text="Сегодня выбрал метро вместо машины", visibility="PUBLIC", moderation_state="Published", reports_count=0, created_at=now - timedelta(hours=1)),
                Post(user_id=user.id, author_name="Ая", text="Сортирую отходы уже 5 дней подряд", visibility="PUBLIC", moderation_state="Needs review", reports_count=2, created_at=now - timedelta(hours=3)),
            ]
        )
    if not db.scalar(select(ChatMessage).where(ChatMessage.user_id == user.id)):
        db.add(ChatMessage(user_id=user.id, role="assistant", text="Привет! Я эко-ИИ. Помогу улучшить твои экопривычки и мотивацию.", created_at=now))
    db.commit()
