from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.admin import EcoCategory, Habit
from app.models.challenge import Challenge, UserChallenge
from app.models.chat import ChatMessage
from app.models.post import Post
from app.models.user import Activity, User
from app.services.auth import hash_password
from app.services.bootstrap import unlocked_challenge_count


CHALLENGE_SPECS = [
    ("Эко-новичок", "Использовать многоразовую бутылку 10 раз", 10, 50, "waterbottle.fill", 0x1AA5E6, 0xE7F5FF),
    ("Неделя силы", "7 раз пройти пешком вместо такси", 7, 70, "figure.walk.circle.fill", 0xF09A00, 0xFFF5E2),
    ("Экономист", "30 дней подряд отмечать экономию электроэнергии", 30, 150, "bolt.fill", 0xF6C300, 0xFFF7D6),
    ("Мастер сортировки", "Отсортировать мусор 40 раз", 40, 120, "arrow.triangle.2.circlepath", 0x4F8DF4, 0xE9F2FF),
    ("Зеленый наставник", "50 дней сокращать время душа на 2-3 минуты", 50, 200, "drop.fill", 0x11A7D8, 0xE6F7FF),
    ("Друг природы", "Подписаться на 10 пользователей", 10, 60, "person.2.fill", 0x7C5CFC, 0xF0EBFF),
    ("Вдохновитель", "Опубликовать 5 постов", 5, 80, "text.bubble.fill", 0xFF6B35, 0xFFF0E8),
    ("Эко-комментатор", "Оставить 20 комментариев", 20, 60, "bubble.left.fill", 0x5E8BFF, 0xEBF1FF),
    ("Любимец сообщества", "Получить 25 лайков на постах", 25, 100, "heart.fill", 0xFF4D6D, 0xFFE7ED),
    ("Стабильный шаг", "Выполнять активности 7 дней подряд", 7, 70, "flame.fill", 0xF97316, 0xFFF0E3),
    ("Зеленая серия", "Выполнять активности 30 дней подряд", 30, 200, "leaf.fill", 0x43B244, 0xEAF8DF),
    ("Бережливый пользователь", "Сэкономить 500 литров воды", 500, 100, "drop.circle.fill", 0x149DDD, 0xE8F7FF),
    ("Энерго-герой", "Сэкономить 100 кВт·ч энергии", 100, 120, "bolt.circle.fill", 0xE7A700, 0xFFF6D9),
    ("Спасатель климата", "Сократить 100 кг CO2", 100, 150, "wind", 0x2F80ED, 0xE7F0FF),
    ("Переработчик", "Переработать 50 единиц отходов", 50, 90, "arrow.3.trianglepath", 0x0FB56A, 0xE7FAEE),
]

CHALLENGE_UNLOCK_ORDER = [item[0] for item in CHALLENGE_SPECS]

CATEGORY_SPECS = [
    ("Энергия", "Energy & electricity", "#F5B100", "bolt"),
    ("Вода", "Water conservation", "#1AA5E6", "drop"),
    ("Пластик", "Plastic reduction", "#43B244", "leaf"),
    ("Транспорт", "Sustainable transport", "#F09A00", "figure.walk"),
    ("Отходы", "Waste reduction", "#8E8E93", "trash"),
]

HABIT_SPECS = [
    ("Пешая прогулка", "Транспорт", 20, 1.5, 0.0, 0.0),
    ("Мотоцикл", "Транспорт", 5, 0.2, 0.0, 0.0),
    ("Велосипед", "Транспорт", 25, 2.0, 0.0, 0.0),
    ("Самокат", "Транспорт", 15, 0.8, 0.0, 0.0),
    ("Машина", "Транспорт", 0, 0.0, 0.0, 0.0),
    ("Общ. транспорт", "Транспорт", 15, 1.0, 0.0, 0.0),
    ("Поезд", "Транспорт", 15, 1.2, 0.0, 0.0),
    ("Совместная поездка", "Транспорт", 18, 1.3, 0.0, 0.0),
    ("Короткий душ", "Вода", 15, 0.35, 25.0, 0.0),
    ("Закрыл кран вовремя", "Вода", 10, 0.08, 8.0, 0.0),
    ("Полная загрузка стирки", "Вода", 20, 0.25, 40.0, 0.0),
    ("Устранил утечку", "Вода", 30, 0.6, 60.0, 0.0),
    ("Установил аэратор", "Вода", 25, 0.45, 35.0, 0.0),
    ("Без пакета", "Пластик", 10, 0.05, 0.0, 0.0),
    ("Многоразовая сумка", "Пластик", 15, 0.08, 0.0, 0.0),
    ("Многоразовая бутылка", "Пластик", 20, 0.12, 0.0, 0.0),
    ("Сдал пластик", "Пластик", 25, 0.18, 0.0, 0.0),
    ("Сортировка", "Отходы", 15, 0.2, 0.0, 0.0),
    ("Сдал вторсырье", "Отходы", 20, 0.3, 0.0, 0.0),
    ("Компост", "Отходы", 20, 0.25, 0.0, 0.0),
    ("Выключил свет", "Энергия", 10, 0.18, 0.0, 2.0),
    ("Отключил приборы из сети", "Энергия", 15, 0.12, 0.0, 3.0),
    ("Использую LED-лампы", "Энергия", 20, 0.4, 0.0, 5.0),
    ("Использую дневной свет", "Энергия", 15, 0.15, 0.0, 3.0),
]

LEGACY_CHALLENGE_TITLES = [
    "7 эко-действий за неделю",
    "3 дня без пластика",
    "Эко-транспорт",
    "Водный баланс",
    "Энергия под контролем",
    "Неделя сортировки",
    "Эко-утро",
    "Чистый воздух",
    "Многоразовый герой",
    "Осознанный шопинг",
    "Эко-комьюнити",
    "Зеленая неделя",
    "Ноль отходов",
    "Дом без потерь",
    "Эко-мастер",
]


def assign_challenges_for_user(db: Session, user: User, challenges: list[Challenge]) -> None:
    unlocked_count = min(unlocked_challenge_count(user.points), len(challenges))
    order_map = {title: index for index, title in enumerate(CHALLENGE_UNLOCK_ORDER)}
    unlocked_challenges = sorted(
        challenges,
        key=lambda item: order_map.get(item.title, len(order_map)),
    )[:unlocked_count]
    existing_by_challenge_id = {
        item.challenge_id
        for item in db.scalars(
            select(UserChallenge).where(UserChallenge.user_id == user.id)
        ).all()
    }
    for challenge in unlocked_challenges:
        if challenge.id in existing_by_challenge_id:
            continue
        db.add(
            UserChallenge(
                user_id=user.id,
                challenge_id=challenge.id,
                current_count=0,
                is_completed=False,
            )
        )


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

    allowed_challenge_titles = {item[0] for item in CHALLENGE_SPECS}
    for challenge in db.scalars(select(Challenge)).all():
        if challenge.title not in allowed_challenge_titles:
            db.delete(challenge)
    db.flush()

    challenges: list[Challenge] = []
    for (
        title,
        description,
        target_count,
        reward_points,
        badge_symbol,
        badge_tint_hex,
        badge_background_hex,
    ) in CHALLENGE_SPECS:
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
        else:
            challenge.description = description
            challenge.target_count = target_count
            challenge.reward_points = reward_points
            challenge.badge_symbol = badge_symbol
            challenge.badge_tint_hex = badge_tint_hex
            challenge.badge_background_hex = badge_background_hex
        challenges.append(challenge)

    allowed_category_names = {item[0] for item in CATEGORY_SPECS}
    for category in db.scalars(select(EcoCategory)).all():
        if category.name not in allowed_category_names:
            db.delete(category)
    db.flush()

    categories: list[EcoCategory] = []
    for name, description, color, icon in CATEGORY_SPECS:
        category = db.scalar(select(EcoCategory).where(EcoCategory.name == name))
        if not category:
            category = EcoCategory(
                name=name,
                description=description,
                color=color,
                icon=icon,
            )
            db.add(category)
            db.flush()
        else:
            category.description = description
            category.color = color
            category.icon = icon
        categories.append(category)

    category_by_name = {item.name: item for item in categories}
    allowed_habit_titles = {item[0] for item in HABIT_SPECS}

    for habit in db.scalars(select(Habit)).all():
        if habit.title not in allowed_habit_titles:
            db.delete(habit)
    db.flush()

    for title, category_name, points, co2_value, water_value, energy_value in HABIT_SPECS:
        habit = db.scalar(select(Habit).where(Habit.title == title))
        if not habit:
            habit = Habit(
                title=title,
                description=f"{category_name} activity",
                points=points,
                co2_value=co2_value,
                water_value=water_value,
                energy_value=energy_value,
                category_id=category_by_name[category_name].id,
            )
            db.add(habit)
        else:
            habit.description = f"{category_name} activity"
            habit.points = points
            habit.co2_value = co2_value
            habit.water_value = water_value
            habit.energy_value = energy_value
            habit.category_id = category_by_name[category_name].id

    assign_challenges_for_user(db, user, challenges)

    user_challenges_by_title = {
        item.challenge.title: item
        for item in db.scalars(
            select(UserChallenge)
            .join(UserChallenge.challenge)
            .where(UserChallenge.user_id == user.id)
        ).all()
    }
    if "Эко-новичок" in user_challenges_by_title:
        user_challenges_by_title["Эко-новичок"].current_count = max(
            user_challenges_by_title["Эко-новичок"].current_count,
            1,
        )
    if "Неделя силы" in user_challenges_by_title:
        user_challenges_by_title["Неделя силы"].current_count = max(
            user_challenges_by_title["Неделя силы"].current_count,
            1,
        )
    if "Стабильный шаг" in user_challenges_by_title:
        user_challenges_by_title["Стабильный шаг"].current_count = max(
            user_challenges_by_title["Стабильный шаг"].current_count,
            2,
        )

    now = datetime.now(timezone.utc)
    if not db.scalar(select(Activity).where(Activity.user_id == user.id)):
        db.add_all(
            [
                Activity(
                    user_id=user.id,
                    category="Энергия",
                    title="Отключил приборы из сети",
                    co2_saved=0.12,
                    points=15,
                    created_at=now - timedelta(hours=20),
                ),
                Activity(
                    user_id=user.id,
                    category="Пластик",
                    title="Многоразовая сумка",
                    co2_saved=0.08,
                    points=15,
                    created_at=now - timedelta(hours=44),
                ),
                Activity(
                    user_id=user.id,
                    category="Транспорт",
                    title="Пешая прогулка",
                    co2_saved=1.5,
                    points=20,
                    created_at=now - timedelta(hours=68),
                ),
                Activity(
                    user_id=user.id,
                    category="Вода",
                    title="Короткий душ",
                    co2_saved=0.35,
                    points=15,
                    created_at=now - timedelta(hours=92),
                ),
            ]
        )
    if not db.scalar(select(Post).where(Post.user_id == user.id)):
        db.add_all(
            [
                Post(
                    user_id=user.id,
                    author_name="Нурс",
                    text="Сегодня выбрал метро вместо машины",
                    visibility="PUBLIC",
                    moderation_state="Published",
                    reports_count=0,
                    created_at=now - timedelta(hours=1),
                ),
                Post(
                    user_id=user.id,
                    author_name="Ая",
                    text="Сортирую отходы уже 5 дней подряд",
                    visibility="PUBLIC",
                    moderation_state="Needs review",
                    reports_count=2,
                    created_at=now - timedelta(hours=3),
                ),
            ]
        )
    if not db.scalar(select(ChatMessage).where(ChatMessage.user_id == user.id)):
        db.add(
            ChatMessage(
                user_id=user.id,
                role="assistant",
                text="Привет! Я эко-ИИ. Помогу улучшить твои экопривычки и мотивацию.",
                created_at=now,
            )
        )
    db.commit()
