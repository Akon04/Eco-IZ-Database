#!/usr/bin/env python3
import argparse
import base64
import hashlib
import json
import os
import secrets
import threading
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import psycopg
from psycopg.rows import dict_row


DEFAULT_DATABASE_URL = "postgresql://ecoiz:ecoiz_password@localhost:5432/ecoiz"

CATEGORY_NAME_MAP = {
    "transport": "Транспорт",
    "water": "Вода",
    "plastic": "Пластик",
    "waste": "Отходы",
    "electricity": "Энергия",
}

REVERSE_CATEGORY_NAME_MAP = {value: key for key, value in CATEGORY_NAME_MAP.items()}

ACHIEVEMENT_STYLE = {
    "Эко-новичок": ("waterbottle.fill", 0x1AA5E6, 0xE7F5FF),
    "Неделя силы": ("figure.walk.circle.fill", 0xF09A00, 0xFFF5E2),
    "Экономист": ("bolt.fill", 0xF6C300, 0xFFF7D6),
    "Мастер сортировки": ("arrow.triangle.2.circlepath", 0x4F8DF4, 0xE9F2FF),
    "Зеленый наставник": ("drop.fill", 0x11A7D8, 0xE6F7FF),
    "Друг природы": ("person.2.fill", 0x7C5CFC, 0xF0EBFF),
    "Вдохновитель": ("text.bubble.fill", 0xFF6B35, 0xFFF0E8),
    "Эко-комментатор": ("bubble.left.fill", 0x5E8BFF, 0xEBF1FF),
    "Любимец сообщества": ("heart.fill", 0xFF4D6D, 0xFFE7ED),
    "Стабильный шаг": ("flame.fill", 0xF97316, 0xFFF0E3),
    "Зеленая серия": ("leaf.fill", 0x43B244, 0xEAF8DF),
    "Бережливый пользователь": ("drop.circle.fill", 0x149DDD, 0xE8F7FF),
    "Энерго-герой": ("bolt.circle.fill", 0xE7A700, 0xFFF6D9),
    "Спасатель климата": ("wind", 0x2F80ED, 0xE7F0FF),
    "Переработчик": ("arrow.3.trianglepath", 0x0FB56A, 0xE7FAEE),
}

LEVELS = [
    (1, "Эко-новичок", 0, 199),
    (2, "Эко-исследователь", 200, 399),
    (3, "Эко-помощник", 400, 699),
    (4, "Хранитель природы", 700, 1099),
    (5, "Зеленый герой", 1100, 1599),
    (6, "Эко-наставник", 1600, 2199),
    (7, "Защитник планеты", 2200, 2999),
    (8, "Мастер устойчивости", 3000, 3999),
    (9, "Амбассадор Eco Iz", 4000, 5499),
    (10, "Хранитель Земли", 5500, 10**9),
]


def iso_now() -> str:
    return datetime.now(UTC).isoformat()


def with_hours_offset(hours: int) -> str:
    return (datetime.now(UTC) + timedelta(hours=hours)).isoformat()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def normalized_username(source: str) -> str:
    base = "".join(char.lower() for char in source if char.isalnum() or char == "_")
    return base or f"user_{uuid.uuid4().hex[:6]}"


def level_number(points: int) -> int:
    for number, _, lower, upper in LEVELS:
        if lower <= points <= upper:
            return number
    return LEVELS[-1][0]


def level_name(points: int) -> str:
    for _, name, lower, upper in LEVELS:
        if lower <= points <= upper:
            return name
    return LEVELS[-1][1]


def day_key(date_value: datetime) -> datetime:
    return date_value.astimezone(UTC).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)


def activity_streak(dates: list[datetime]) -> int:
    if not dates:
        return 0
    distinct_days = sorted({day_key(item) for item in dates}, reverse=True)
    streak = 1
    for previous, current in zip(distinct_days, distinct_days[1:]):
        if previous - current == timedelta(days=1):
            streak += 1
        else:
            break
    return streak


def ai_response(text: str) -> str:
    lowercase = text.lower()
    if "вод" in lowercase:
        return "Попробуй 5-минутный душ и проверь, нет ли протечек. Это дает стабильный эффект каждый день."
    if "транспорт" in lowercase or "машин" in lowercase:
        return "2-3 поездки в неделю на метро, автобусе или велосипеде уже заметно снижают личный след CO₂."
    if "мотивац" in lowercase or "сложно" in lowercase:
        return "Сфокусируйся на серии: одно небольшое действие в день лучше, чем идеальный, но редкий рывок."
    return "Отличный вопрос. Держи ритм: выбери 1 активити из воды, 1 из энергии и 1 из пластика сегодня."


class PostgresStore:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url
        self.lock = threading.Lock()
        self._initialize()

    def _connect(self) -> psycopg.Connection:
        return psycopg.connect(self.database_url, row_factory=dict_row)

    def _initialize(self) -> None:
        with self._connect() as db:
            db.execute("SELECT 1")
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS app_post_media (
                    id TEXT PRIMARY KEY,
                    "postId" TEXT NOT NULL REFERENCES "post"("id") ON DELETE CASCADE,
                    kind TEXT NOT NULL,
                    "dataBase64" TEXT NOT NULL
                )
                """
            )
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS app_ai_chat_message (
                    id TEXT PRIMARY KEY,
                    "userId" TEXT NOT NULL REFERENCES "user"("id") ON DELETE CASCADE,
                    "isUser" BOOLEAN NOT NULL,
                    text TEXT NOT NULL,
                    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            db.commit()
        self._ensure_default_records()

    def _ensure_default_records(self) -> None:
        with self.lock, self._connect() as db:
            self._create_demo_user_if_missing(
                db,
                full_name="Пользователь",
                email="user@ecoiz.app",
                username="ecoiz_user",
                password="password123",
            )
            self._create_demo_user_if_missing(
                db,
                full_name="Нурс",
                email="nurs@ecoiz.app",
                username="nurs",
                password="password123",
            )
            self._create_demo_user_if_missing(
                db,
                full_name="Ая",
                email="aya@ecoiz.app",
                username="aya",
                password="password123",
            )
            self._seed_default_activity_history(db)
            self._seed_default_feed(db)
            db.commit()

    def _create_demo_user_if_missing(
        self,
        db: psycopg.Connection,
        full_name: str,
        email: str,
        username: str,
        password: str,
    ) -> str:
        existing = db.execute('SELECT id FROM "user" WHERE email = %s', (email,)).fetchone()
        if existing:
            user_id = existing["id"]
        else:
            user_id = f"user-{uuid.uuid4().hex[:8]}"
            now = datetime.now(UTC)
            db.execute(
                """
                INSERT INTO "user" ("id", "email", "username", "password", "role", "isEmailVerified", "createdAt", "updatedAt")
                VALUES (%s, %s, %s, %s, 'USER', TRUE, %s, %s)
                """,
                (user_id, email, username, hash_password(password), now, now),
            )
            db.execute(
                """
                INSERT INTO "profile" ("id", "userId", "displayName", "createdAt", "updatedAt")
                VALUES (%s, %s, %s, %s, %s)
                """,
                (f"profile-{uuid.uuid4().hex[:8]}", user_id, full_name, now, now),
            )
            db.execute(
                """
                INSERT INTO "user_stats" ("id", "userId", "level", "ecoPoints", "streakDays", "co2SavedTotal", "waterSavedTotal",
                                          "energySavedTotal", "recycledItemsTotal", "updatedAt", "createdAt")
                VALUES (%s, %s, 1, 0, 0, 0, 0, 0, 0, %s, %s)
                """,
                (f"stats-{uuid.uuid4().hex[:8]}", user_id, now, now),
            )
            achievements = db.execute('SELECT id, "targetValue" FROM "achievement"').fetchall()
            for achievement in achievements:
                db.execute(
                    """
                    INSERT INTO "achievement_progress" ("id", "userId", "achievementId", "currentValue", "targetValue", "updatedAt", "createdAt")
                    VALUES (%s, %s, %s, 0, %s, %s, %s)
                    ON CONFLICT ("userId", "achievementId") DO NOTHING
                    """,
                    (
                        f"achievement-progress-{uuid.uuid4().hex[:8]}",
                        user_id,
                        achievement["id"],
                        achievement["targetValue"],
                        now,
                        now,
                    ),
                )
            db.execute(
                """
                INSERT INTO app_ai_chat_message ("id", "userId", "isUser", "text", "createdAt")
                VALUES (%s, %s, FALSE, %s, %s)
                ON CONFLICT DO NOTHING
                """,
                (
                    f"chat-{uuid.uuid4().hex[:8]}",
                    user_id,
                    "Привет! Я эко-ИИ. Помогу улучшить твои экопривычки и мотивацию.",
                    now,
                ),
            )
        return user_id

    def _seed_default_activity_history(self, db: psycopg.Connection) -> None:
        main_user = db.execute('SELECT id FROM "user" WHERE email = %s', ("user@ecoiz.app",)).fetchone()
        if not main_user:
            return
        existing_logs = db.execute('SELECT COUNT(*) AS count FROM "habit_log" WHERE "userId" = %s', (main_user["id"],)).fetchone()
        if existing_logs["count"] > 0:
            return

        demo_logs = [
            ("Отключил приборы из сети", 15, 0.0, 0.0, 3.0, 0, with_hours_offset(-20)),
            ("Многоразовая сумка", 15, 0.0, 0.0, 0.0, 1, with_hours_offset(-44)),
            ("Пешая прогулка", 20, 1.5, 0.0, 0.0, 0, with_hours_offset(-68)),
            ("Короткий душ", 15, 0.0, 25.0, 0.0, 0, with_hours_offset(-92)),
            ("Сортировка", 15, 0.0, 0.0, 0.0, 2, with_hours_offset(-116)),
            ("Использую дневной свет", 15, 0.0, 0.0, 3.0, 0, with_hours_offset(-140)),
        ]

        for title, points, co2, water, energy, recycled, performed_at in demo_logs:
            habit = self._habit_by_title(db, title)
            if not habit:
                continue
            user_habit_id = self._ensure_user_habit(db, main_user["id"], habit["id"])
            now = datetime.now(UTC)
            db.execute(
                """
                INSERT INTO "habit_log" ("id", "userHabitId", "userId", "habitId", "pointsEarned", "co2Saved", "waterSaved",
                                         "energySaved", "recycledItems", "performedAt", "createdAt")
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    f"log-{uuid.uuid4().hex[:8]}",
                    user_habit_id,
                    main_user["id"],
                    habit["id"],
                    points,
                    co2,
                    water,
                    energy,
                    recycled,
                    performed_at,
                    now,
                ),
            )
            self._upsert_daily_stat(db, main_user["id"], datetime.fromisoformat(performed_at), points, co2, water, energy, recycled)

        self._refresh_achievement_progress(db, main_user["id"])
        self._refresh_user_stats(db, main_user["id"])

    def _seed_default_feed(self, db: psycopg.Connection) -> None:
        posts_count = db.execute('SELECT COUNT(*) AS count FROM "post"').fetchone()
        if posts_count["count"] > 0:
            return

        demo_posts = [
            ("nurs@ecoiz.app", "Сегодня выбрал метро вместо машины", with_hours_offset(-1)),
            ("aya@ecoiz.app", "Сортирую отходы уже 5 дней подряд", with_hours_offset(-3)),
        ]
        for email, content, created_at in demo_posts:
            user = db.execute(
                """
                SELECT u.id, COALESCE(p."displayName", u.username) AS name
                FROM "user" u
                LEFT JOIN "profile" p ON p."userId" = u.id
                WHERE u.email = %s
                """,
                (email,),
            ).fetchone()
            if not user:
                continue
            db.execute(
                """
                INSERT INTO "post" ("id", "authorId", "content", "visibility", "createdAt", "updatedAt")
                VALUES (%s, %s, %s, 'PUBLIC', %s, %s)
                """,
                (f"post-{uuid.uuid4().hex[:8]}", user["id"], content, created_at, created_at),
            )

    def authenticate(self, token: str | None) -> dict[str, Any] | None:
        if not token:
            return None
        with self._connect() as db:
            row = db.execute(
                """
                SELECT u.id, u.email, u.username,
                       COALESCE(p."displayName", u.username) AS "fullName",
                       COALESCE(s."ecoPoints", 0) AS points,
                       COALESCE(s."streakDays", 0) AS "streakDays",
                       COALESCE(s."co2SavedTotal", 0) AS "co2SavedTotal"
                FROM "refresh_token" rt
                JOIN "user" u ON u.id = rt."userId"
                LEFT JOIN "profile" p ON p."userId" = u.id
                LEFT JOIN "user_stats" s ON s."userId" = u.id
                WHERE rt.token = %s AND rt."expiresAt" > NOW()
                """,
                (token,),
            ).fetchone()
            return self._serialize_user(row) if row else None

    def register(self, full_name: str, email: str, password: str) -> tuple[str, dict[str, Any]]:
        with self.lock, self._connect() as db:
            normalized_email = email.strip().lower()
            existing = db.execute('SELECT id FROM "user" WHERE email = %s', (normalized_email,)).fetchone()
            if existing:
                raise ValueError("User with this email already exists.")

            user_id = self._create_demo_user_if_missing(
                db,
                full_name=full_name.strip(),
                email=normalized_email,
                username=self._unique_username(db, normalized_username(normalized_email.split("@")[0])),
                password=password,
            )
            token = self._create_refresh_token(db, user_id)
            db.commit()
            user = self.authenticate(token)
            return token, user

    def login(self, email: str, password: str) -> tuple[str, dict[str, Any]]:
        with self.lock, self._connect() as db:
            normalized_email = email.strip().lower()
            row = db.execute('SELECT id, password FROM "user" WHERE email = %s', (normalized_email,)).fetchone()
            if not row:
                raise ValueError("Invalid email or password.")
            if row["password"] not in {password, hash_password(password)}:
                raise ValueError("Invalid email or password.")
            token = self._create_refresh_token(db, row["id"])
            db.commit()
            user = self.authenticate(token)
            return token, user

    def snapshot_for(self, user_id: str) -> dict[str, Any]:
        with self._connect() as db:
            return {
                "user": self._user_by_id(db, user_id),
                "activities": self._activities_for(db, user_id),
                "challenges": self._challenges_for(db, user_id),
                "posts": self._posts_for(db),
                "chatMessages": self._chat_messages_for(db, user_id),
            }

    def add_activity(
        self,
        user_id: str,
        category: str,
        title: str,
        co2_saved: float,
        points: int,
        note: str,
        media: list[dict[str, Any]],
        share_to_news: bool,
    ) -> dict[str, Any]:
        with self.lock, self._connect() as db:
            performed_at = datetime.now(UTC)
            habit = self._resolve_habit(db, user_id, category, title)
            user_habit_id = self._ensure_user_habit(db, user_id, habit["id"])
            log_id = f"log-{uuid.uuid4().hex[:8]}"
            db.execute(
                """
                INSERT INTO "habit_log" ("id", "userHabitId", "userId", "habitId", "pointsEarned", "co2Saved", "waterSaved",
                                         "energySaved", "recycledItems", "performedAt", "note", "createdAt")
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    log_id,
                    user_habit_id,
                    user_id,
                    habit["id"],
                    points,
                    co2_saved,
                    habit["waterValue"] if category != "Своя активность" else 0 if category == "Транспорт" else habit["waterValue"],
                    habit["energyValue"] if category != "Своя активность" else 0 if category != "Энергия" else habit["energyValue"],
                    habit["recycledValue"] if category != "Своя активность" else 0,
                    performed_at,
                    note.strip() or None,
                    performed_at,
                ),
            )

            water_saved = float(habit["waterValue"] or 0)
            energy_saved = float(habit["energyValue"] or 0)
            recycled_items = int(habit["recycledValue"] or 0)
            if category == "Своя активность":
                if "вода" in note.lower():
                    water_saved = 5
                if "энерг" in note.lower():
                    energy_saved = 1
                if any(term in note.lower() for term in ["пласт", "сорт", "мусор", "втор"]):
                    recycled_items = 1

            db.execute(
                """
                UPDATE "habit_log"
                SET "waterSaved" = %s, "energySaved" = %s, "recycledItems" = %s
                WHERE id = %s
                """,
                (water_saved, energy_saved, recycled_items, log_id),
            )
            self._upsert_daily_stat(db, user_id, performed_at, points, co2_saved, water_saved, energy_saved, recycled_items)

            if share_to_news:
                post_id = f"post-{uuid.uuid4().hex[:8]}"
                content = f"Добавил активити: {title.strip()} ({category})"
                if note.strip():
                    content = f"{content}\n{note.strip()}"
                db.execute(
                    """
                    INSERT INTO "post" ("id", "authorId", "content", "visibility", "createdAt", "updatedAt")
                    VALUES (%s, %s, %s, 'PUBLIC', %s, %s)
                    """,
                    (post_id, user_id, content, performed_at, performed_at),
                )
                self._insert_post_media(db, post_id, media)

            self._refresh_achievement_progress(db, user_id)
            self._refresh_user_stats(db, user_id)
            db.commit()

            activity = db.execute(
                """
                SELECT hl.id, h.title, h."isCustom", c.name AS category_name, hl."co2Saved", hl."pointsEarned",
                       hl."performedAt"
                FROM "habit_log" hl
                JOIN habits h ON h.id = hl."habitId"
                JOIN eco_category c ON c.id = h."categoryId"
                WHERE hl.id = %s
                """,
                (log_id,),
            ).fetchone()
            return {
                "activity": self._serialize_activity(activity),
                "user": self._user_by_id(db, user_id),
                "challenges": self._challenges_for(db, user_id),
            }

    def add_post(self, user_id: str, text: str, media: list[dict[str, Any]]) -> dict[str, Any]:
        with self.lock, self._connect() as db:
            trimmed = text.strip()
            if not trimmed and not media:
                raise ValueError("Post text or media is required.")
            created_at = datetime.now(UTC)
            post_id = f"post-{uuid.uuid4().hex[:8]}"
            db.execute(
                """
                INSERT INTO "post" ("id", "authorId", "content", "visibility", "createdAt", "updatedAt")
                VALUES (%s, %s, %s, 'PUBLIC', %s, %s)
                """,
                (post_id, user_id, trimmed, created_at, created_at),
            )
            self._insert_post_media(db, post_id, media)
            self._refresh_achievement_progress(db, user_id)
            self._refresh_user_stats(db, user_id)
            db.commit()
            post = db.execute(
                """
                SELECT p.id, p.content, p."createdAt", u.username, COALESCE(pr."displayName", u.username) AS author
                FROM "post" p
                JOIN "user" u ON u.id = p."authorId"
                LEFT JOIN "profile" pr ON pr."userId" = u.id
                WHERE p.id = %s
                """,
                (post_id,),
            ).fetchone()
            return self._serialize_post(db, post)

    def add_chat_message(self, user_id: str, text: str) -> list[dict[str, Any]]:
        with self.lock, self._connect() as db:
            trimmed = text.strip()
            if not trimmed:
                raise ValueError("Message text is required.")
            created_at = datetime.now(UTC)
            user_message_id = f"chat-{uuid.uuid4().hex[:8]}"
            assistant_message_id = f"chat-{uuid.uuid4().hex[:8]}"
            db.execute(
                """
                INSERT INTO app_ai_chat_message ("id", "userId", "isUser", "text", "createdAt")
                VALUES (%s, %s, TRUE, %s, %s)
                """,
                (user_message_id, user_id, trimmed, created_at),
            )
            db.execute(
                """
                INSERT INTO app_ai_chat_message ("id", "userId", "isUser", "text", "createdAt")
                VALUES (%s, %s, FALSE, %s, %s)
                """,
                (assistant_message_id, user_id, ai_response(trimmed), datetime.now(UTC)),
            )
            db.commit()
            rows = db.execute(
                """
                SELECT * FROM app_ai_chat_message
                WHERE id IN (%s, %s)
                ORDER BY "createdAt" ASC
                """,
                (user_message_id, assistant_message_id),
            ).fetchall()
            return [self._serialize_chat_message(row) for row in rows]

    def _create_refresh_token(self, db: psycopg.Connection, user_id: str) -> str:
        token = secrets.token_hex(32)
        now = datetime.now(UTC)
        db.execute(
            """
            INSERT INTO "refresh_token" ("id", "userId", "token", "expiresAt", "createdAt")
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                f"refresh-{uuid.uuid4().hex[:8]}",
                user_id,
                token,
                now + timedelta(days=30),
                now,
            ),
        )
        return token

    def _unique_username(self, db: psycopg.Connection, candidate: str) -> str:
        username = candidate
        suffix = 1
        while db.execute('SELECT 1 FROM "user" WHERE username = %s', (username,)).fetchone():
            username = f"{candidate}{suffix}"
            suffix += 1
        return username

    def _user_by_id(self, db: psycopg.Connection, user_id: str) -> dict[str, Any]:
        row = db.execute(
            """
            SELECT u.id, u.email, u.username,
                   COALESCE(p."displayName", u.username) AS "fullName",
                   COALESCE(s."ecoPoints", 0) AS points,
                   COALESCE(s."streakDays", 0) AS "streakDays",
                   COALESCE(s."co2SavedTotal", 0) AS "co2SavedTotal"
            FROM "user" u
            LEFT JOIN "profile" p ON p."userId" = u.id
            LEFT JOIN "user_stats" s ON s."userId" = u.id
            WHERE u.id = %s
            """,
            (user_id,),
        ).fetchone()
        return self._serialize_user(row)

    def _serialize_user(self, row: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": row["id"],
            "fullName": row["fullName"],
            "email": row["email"],
            "points": int(row["points"] or 0),
            "streakDays": int(row["streakDays"] or 0),
            "co2SavedTotal": float(row["co2SavedTotal"] or 0),
            "level": level_name(int(row["points"] or 0)),
        }

    def _activities_for(self, db: psycopg.Connection, user_id: str) -> list[dict[str, Any]]:
        rows = db.execute(
            """
            SELECT hl.id, h.title, h."isCustom", c.name AS category_name, hl."co2Saved", hl."pointsEarned", hl."performedAt"
            FROM "habit_log" hl
            JOIN habits h ON h.id = hl."habitId"
            JOIN eco_category c ON c.id = h."categoryId"
            WHERE hl."userId" = %s
            ORDER BY hl."performedAt" DESC
            """,
            (user_id,),
        ).fetchall()
        return [self._serialize_activity(row) for row in rows]

    def _serialize_activity(self, row: dict[str, Any]) -> dict[str, Any]:
        category = "Своя активность" if row["isCustom"] else CATEGORY_NAME_MAP.get(row["category_name"], row["category_name"])
        return {
            "id": row["id"],
            "category": category,
            "title": row["title"],
            "co2Saved": float(row["co2Saved"] or 0),
            "points": int(row["pointsEarned"] or 0),
            "createdAt": row["performedAt"].isoformat(),
        }

    def _challenges_for(self, db: psycopg.Connection, user_id: str) -> list[dict[str, Any]]:
        rows = db.execute(
            """
            SELECT ap."currentValue", ap."targetValue", ap."completedAt",
                   a.id, a.title, a.description, a.icon, a."rewardPoints"
            FROM "achievement_progress" ap
            JOIN achievement a ON a.id = ap."achievementId"
            WHERE ap."userId" = %s
            ORDER BY a."createdAt" ASC
            """,
            (user_id,),
        ).fetchall()
        items: list[dict[str, Any]] = []
        for row in rows:
            symbol, tint, background = ACHIEVEMENT_STYLE.get(row["title"], ("leaf.fill", 0x43B244, 0xEAF8DF))
            items.append(
                {
                    "id": row["id"],
                    "title": row["title"],
                    "description": row["description"] or "",
                    "targetCount": int(row["targetValue"]),
                    "currentCount": int(row["currentValue"]),
                    "rewardPoints": int(row["rewardPoints"]),
                    "badgeSymbol": symbol,
                    "badgeTintHex": tint,
                    "badgeBackgroundHex": background,
                    "isCompleted": row["completedAt"] is not None or int(row["currentValue"]) >= int(row["targetValue"]),
                }
            )
        return items

    def _posts_for(self, db: psycopg.Connection) -> list[dict[str, Any]]:
        rows = db.execute(
            """
            SELECT p.id, p.content, p."createdAt", u.username,
                   COALESCE(pr."displayName", u.username) AS author
            FROM "post" p
            JOIN "user" u ON u.id = p."authorId"
            LEFT JOIN "profile" pr ON pr."userId" = u.id
            WHERE p.visibility = 'PUBLIC'
            ORDER BY p."createdAt" DESC
            """,
        ).fetchall()
        return [self._serialize_post(db, row) for row in rows]

    def _serialize_post(self, db: psycopg.Connection, row: dict[str, Any]) -> dict[str, Any]:
        media_rows = db.execute(
            'SELECT id, kind, "dataBase64" FROM app_post_media WHERE "postId" = %s ORDER BY id ASC',
            (row["id"],),
        ).fetchall()
        return {
            "id": row["id"],
            "author": row["author"],
            "text": row["content"],
            "createdAt": row["createdAt"].isoformat(),
            "media": [
                {
                    "id": item["id"],
                    "kind": item["kind"],
                    "base64Data": item["dataBase64"],
                }
                for item in media_rows
            ],
        }

    def _chat_messages_for(self, db: psycopg.Connection, user_id: str) -> list[dict[str, Any]]:
        rows = db.execute(
            """
            SELECT id, "isUser", text, "createdAt"
            FROM app_ai_chat_message
            WHERE "userId" = %s
            ORDER BY "createdAt" ASC
            """,
            (user_id,),
        ).fetchall()
        if not rows:
            now = datetime.now(UTC)
            db.execute(
                """
                INSERT INTO app_ai_chat_message ("id", "userId", "isUser", "text", "createdAt")
                VALUES (%s, %s, FALSE, %s, %s)
                """,
                (f"chat-{uuid.uuid4().hex[:8]}", user_id, "Привет! Я эко-ИИ. Помогу улучшить твои экопривычки и мотивацию.", now),
            )
            db.commit()
            rows = db.execute(
                """
                SELECT id, "isUser", text, "createdAt"
                FROM app_ai_chat_message
                WHERE "userId" = %s
                ORDER BY "createdAt" ASC
                """,
                (user_id,),
            ).fetchall()
        return [self._serialize_chat_message(row) for row in rows]

    def _serialize_chat_message(self, row: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": row["id"],
            "isUser": bool(row["isUser"]),
            "text": row["text"],
            "createdAt": row["createdAt"].isoformat(),
        }

    def _insert_post_media(self, db: psycopg.Connection, post_id: str, media: list[dict[str, Any]]) -> None:
        for item in media:
            data_base64 = str(item.get("base64Data", "")).strip()
            if not data_base64:
                continue
            try:
                base64.b64decode(data_base64.encode("utf-8"))
            except Exception:
                continue
            db.execute(
                """
                INSERT INTO app_post_media (id, "postId", kind, "dataBase64")
                VALUES (%s, %s, %s, %s)
                """,
                (str(item.get("id") or f"media-{uuid.uuid4().hex[:8]}"), post_id, str(item.get("kind") or "photo"), data_base64),
            )

    def _habit_by_title(self, db: psycopg.Connection, title: str) -> dict[str, Any] | None:
        return db.execute(
            """
            SELECT h.id, h.title, h."isCustom", h."waterValue", h."energyValue", h."recycledValue",
                   c.name AS category_name
            FROM habits h
            JOIN eco_category c ON c.id = h."categoryId"
            WHERE h.title = %s
            LIMIT 1
            """,
            (title,),
        ).fetchone()

    def _resolve_habit(self, db: psycopg.Connection, user_id: str, category: str, title: str) -> dict[str, Any]:
        base_title = title.split("•")[0].strip()
        if category == "Своя активность":
            existing = db.execute(
                """
                SELECT h.id, h.title, h."isCustom", h."waterValue", h."energyValue", h."recycledValue",
                       c.name AS category_name
                FROM habits h
                JOIN eco_category c ON c.id = h."categoryId"
                WHERE h.title = %s AND h."creatorId" = %s
                LIMIT 1
                """,
                (title.strip(), user_id),
            ).fetchone()
            if existing:
                return existing
            waste_category = db.execute('SELECT id FROM eco_category WHERE name = %s', ("waste",)).fetchone()
            now = datetime.now(UTC)
            habit_id = f"habit-{uuid.uuid4().hex[:8]}"
            db.execute(
                """
                INSERT INTO habits ("id", title, description, icon, points, "co2Value", "waterValue", "energyValue",
                                    "recycledValue", "isCustom", "categoryId", "creatorId", "createdAt", "updatedAt")
                VALUES (%s, %s, %s, %s, 10, 0, 0, 0, 1, TRUE, %s, %s, %s, %s)
                """,
                (habit_id, title.strip(), "Custom habit", "sparkles", waste_category["id"], user_id, now, now),
            )
            return {
                "id": habit_id,
                "title": title.strip(),
                "isCustom": True,
                "waterValue": 0,
                "energyValue": 0,
                "recycledValue": 1,
                "category_name": "waste",
            }

        category_key = REVERSE_CATEGORY_NAME_MAP.get(category, "waste")
        row = db.execute(
            """
            SELECT h.id, h.title, h."isCustom", h."waterValue", h."energyValue", h."recycledValue",
                   c.name AS category_name
            FROM habits h
            JOIN eco_category c ON c.id = h."categoryId"
            WHERE c.name = %s AND (h.title = %s OR h.title = %s)
            ORDER BY h."isCustom" ASC
            LIMIT 1
            """,
            (category_key, title.strip(), base_title),
        ).fetchone()
        if row:
            return row

        category_row = db.execute('SELECT id FROM eco_category WHERE name = %s', (category_key,)).fetchone()
        now = datetime.now(UTC)
        habit_id = f"habit-{uuid.uuid4().hex[:8]}"
        db.execute(
            """
            INSERT INTO habits ("id", title, description, icon, points, "co2Value", "waterValue", "energyValue",
                                "recycledValue", "isCustom", "categoryId", "creatorId", "createdAt", "updatedAt")
            VALUES (%s, %s, %s, %s, 10, 0, 0, 0, 0, TRUE, %s, %s, %s, %s)
            """,
            (habit_id, title.strip(), "Generated habit", title.strip(), category_row["id"], user_id, now, now),
        )
        return {
            "id": habit_id,
            "title": title.strip(),
            "isCustom": True,
            "waterValue": 0,
            "energyValue": 0,
            "recycledValue": 0,
            "category_name": category_key,
        }

    def _ensure_user_habit(self, db: psycopg.Connection, user_id: str, habit_id: str) -> str:
        existing = db.execute(
            'SELECT id FROM "user_habit" WHERE "userId" = %s AND "habitId" = %s',
            (user_id, habit_id),
        ).fetchone()
        if existing:
            return existing["id"]
        now = datetime.now(UTC)
        user_habit_id = f"user-habit-{uuid.uuid4().hex[:8]}"
        db.execute(
            """
            INSERT INTO "user_habit" ("id", "userId", "habitId", "startDate", status, "createdAt", "updatedAt")
            VALUES (%s, %s, %s, %s, 'ACTIVE', %s, %s)
            """,
            (user_habit_id, user_id, habit_id, now, now, now),
        )
        return user_habit_id

    def _upsert_daily_stat(
        self,
        db: psycopg.Connection,
        user_id: str,
        performed_at: datetime,
        points: int,
        co2_saved: float,
        water_saved: float,
        energy_saved: float,
        recycled_items: int,
    ) -> None:
        stat_date = day_key(performed_at)
        existing = db.execute(
            'SELECT id FROM "daily_stat" WHERE "userId" = %s AND date = %s',
            (user_id, stat_date),
        ).fetchone()
        now = datetime.now(UTC)
        if existing:
            db.execute(
                """
                UPDATE "daily_stat"
                SET "pointsEarned" = "pointsEarned" + %s,
                    "co2Saved" = "co2Saved" + %s,
                    "waterSaved" = "waterSaved" + %s,
                    "energySaved" = "energySaved" + %s,
                    "recycledItems" = "recycledItems" + %s,
                    "updatedAt" = %s
                WHERE id = %s
                """,
                (points, co2_saved, water_saved, energy_saved, recycled_items, now, existing["id"]),
            )
        else:
            db.execute(
                """
                INSERT INTO "daily_stat" ("id", "userId", date, "pointsEarned", "co2Saved", "waterSaved",
                                          "energySaved", "recycledItems", "createdAt", "updatedAt")
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (f"daily-{uuid.uuid4().hex[:8]}", user_id, stat_date, points, co2_saved, water_saved, energy_saved, recycled_items, now, now),
            )

    def _refresh_user_stats(self, db: psycopg.Connection, user_id: str) -> None:
        log_aggregate = db.execute(
            """
            SELECT COALESCE(SUM("pointsEarned"), 0) AS points,
                   COALESCE(SUM("co2Saved"), 0) AS co2,
                   COALESCE(SUM("waterSaved"), 0) AS water,
                   COALESCE(SUM("energySaved"), 0) AS energy,
                   COALESCE(SUM("recycledItems"), 0) AS recycled
            FROM "habit_log"
            WHERE "userId" = %s
            """,
            (user_id,),
        ).fetchone()
        reward_points = db.execute(
            """
            SELECT COALESCE(SUM(a."rewardPoints"), 0) AS reward
            FROM "user_achievement" ua
            JOIN achievement a ON a.id = ua."achievementId"
            WHERE ua."userId" = %s
            """,
            (user_id,),
        ).fetchone()["reward"]
        dates = db.execute(
            'SELECT "performedAt" FROM "habit_log" WHERE "userId" = %s ORDER BY "performedAt" DESC',
            (user_id,),
        ).fetchall()
        streak = activity_streak([row["performedAt"] for row in dates])
        eco_points = int(log_aggregate["points"]) + int(reward_points or 0)
        now = datetime.now(UTC)
        existing = db.execute('SELECT id FROM "user_stats" WHERE "userId" = %s', (user_id,)).fetchone()
        if existing:
            db.execute(
                """
                UPDATE "user_stats"
                SET level = %s,
                    "ecoPoints" = %s,
                    "streakDays" = %s,
                    "co2SavedTotal" = %s,
                    "waterSavedTotal" = %s,
                    "energySavedTotal" = %s,
                    "recycledItemsTotal" = %s,
                    "updatedAt" = %s
                WHERE "userId" = %s
                """,
                (
                    level_number(eco_points),
                    eco_points,
                    streak,
                    float(log_aggregate["co2"] or 0),
                    float(log_aggregate["water"] or 0),
                    float(log_aggregate["energy"] or 0),
                    int(log_aggregate["recycled"] or 0),
                    now,
                    user_id,
                ),
            )
        else:
            db.execute(
                """
                INSERT INTO "user_stats" ("id", "userId", level, "ecoPoints", "streakDays", "co2SavedTotal", "waterSavedTotal",
                                          "energySavedTotal", "recycledItemsTotal", "updatedAt", "createdAt")
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    f"stats-{uuid.uuid4().hex[:8]}",
                    user_id,
                    level_number(eco_points),
                    eco_points,
                    streak,
                    float(log_aggregate["co2"] or 0),
                    float(log_aggregate["water"] or 0),
                    float(log_aggregate["energy"] or 0),
                    int(log_aggregate["recycled"] or 0),
                    now,
                    now,
                ),
            )

    def _refresh_achievement_progress(self, db: psycopg.Connection, user_id: str) -> None:
        metrics = self._achievement_metrics(db, user_id)
        achievements = db.execute('SELECT id, title, "targetValue" FROM achievement ORDER BY "createdAt" ASC').fetchall()
        now = datetime.now(UTC)
        for achievement in achievements:
            current_value = metrics.get(achievement["title"], 0)
            db.execute(
                """
                UPDATE "achievement_progress"
                SET "currentValue" = %s,
                    "targetValue" = %s,
                    "completedAt" = CASE
                        WHEN %s >= "targetValue" AND "completedAt" IS NULL THEN %s
                        WHEN %s < "targetValue" THEN NULL
                        ELSE "completedAt"
                    END,
                    "updatedAt" = %s
                WHERE "userId" = %s AND "achievementId" = %s
                """,
                (current_value, achievement["targetValue"], current_value, now, current_value, now, user_id, achievement["id"]),
            )
            if current_value >= achievement["targetValue"]:
                db.execute(
                    """
                    INSERT INTO "user_achievement" ("id", "userId", "achievementId", "obtainedAt")
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT ("userId", "achievementId") DO NOTHING
                    """,
                    (f"user-achievement-{uuid.uuid4().hex[:8]}", user_id, achievement["id"], now),
                )

    def _achievement_metrics(self, db: psycopg.Connection, user_id: str) -> dict[str, int]:
        habit_counts = {
            row["title"]: int(row["count"])
            for row in db.execute(
                """
                SELECT h.title, COUNT(*) AS count
                FROM "habit_log" hl
                JOIN habits h ON h.id = hl."habitId"
                WHERE hl."userId" = %s
                GROUP BY h.title
                """,
                (user_id,),
            ).fetchall()
        }
        post_count = db.execute('SELECT COUNT(*) AS count FROM "post" WHERE "authorId" = %s', (user_id,)).fetchone()["count"]
        comment_count = db.execute('SELECT COUNT(*) AS count FROM "post_comment" WHERE "authorId" = %s', (user_id,)).fetchone()["count"]
        follow_count = db.execute('SELECT COUNT(*) AS count FROM "user_follow" WHERE "followerId" = %s', (user_id,)).fetchone()["count"]
        received_like_count = db.execute(
            """
            SELECT COUNT(*) AS count
            FROM "post_like" pl
            JOIN "post" p ON p.id = pl."postId"
            WHERE p."authorId" = %s
            """,
            (user_id,),
        ).fetchone()["count"]
        stat_row = db.execute(
            """
            SELECT COALESCE("streakDays", 0) AS streak, COALESCE("waterSavedTotal", 0) AS water,
                   COALESCE("energySavedTotal", 0) AS energy, COALESCE("co2SavedTotal", 0) AS co2,
                   COALESCE("recycledItemsTotal", 0) AS recycled
            FROM "user_stats" WHERE "userId" = %s
            """,
            (user_id,),
        ).fetchone()
        if not stat_row:
            log_row = db.execute(
                """
                SELECT COALESCE(SUM("waterSaved"), 0) AS water,
                       COALESCE(SUM("energySaved"), 0) AS energy,
                       COALESCE(SUM("co2Saved"), 0) AS co2,
                       COALESCE(SUM("recycledItems"), 0) AS recycled
                FROM "habit_log" WHERE "userId" = %s
                """,
                (user_id,),
            ).fetchone()
            streak_total = activity_streak(
                [row["performedAt"] for row in db.execute('SELECT "performedAt" FROM "habit_log" WHERE "userId" = %s ORDER BY "performedAt" DESC', (user_id,)).fetchall()]
            )
            water_total = int(log_row["water"] or 0)
            energy_total = int(log_row["energy"] or 0)
            co2_total = int(log_row["co2"] or 0)
            recycled_total = int(log_row["recycled"] or 0)
        else:
            streak_total = int(stat_row["streak"])
            water_total = int(float(stat_row["water"]))
            energy_total = int(float(stat_row["energy"]))
            co2_total = int(float(stat_row["co2"]))
            recycled_total = int(stat_row["recycled"])

        electricity_dates = [
            row["performedAt"]
            for row in db.execute(
                """
                SELECT hl."performedAt"
                FROM "habit_log" hl
                JOIN habits h ON h.id = hl."habitId"
                JOIN eco_category c ON c.id = h."categoryId"
                WHERE hl."userId" = %s AND c.name = 'electricity'
                ORDER BY hl."performedAt" DESC
                """,
                (user_id,),
            ).fetchall()
        ]
        electricity_streak = activity_streak(electricity_dates)

        return {
            "Эко-новичок": habit_counts.get("Многоразовая бутылка", 0),
            "Неделя силы": habit_counts.get("Пешая прогулка", 0),
            "Экономист": electricity_streak,
            "Мастер сортировки": habit_counts.get("Сортировка", 0),
            "Зеленый наставник": habit_counts.get("Короткий душ", 0),
            "Друг природы": int(follow_count),
            "Вдохновитель": int(post_count),
            "Эко-комментатор": int(comment_count),
            "Любимец сообщества": int(received_like_count),
            "Стабильный шаг": streak_total,
            "Зеленая серия": streak_total,
            "Бережливый пользователь": water_total,
            "Энерго-герой": energy_total,
            "Спасатель климата": co2_total,
            "Переработчик": recycled_total,
        }


@dataclass
class AppContext:
    store: PostgresStore


class EcoRequestHandler(BaseHTTPRequestHandler):
    server_version = "EcoIZBackend/2.0"

    def do_OPTIONS(self) -> None:
        self._send_json(HTTPStatus.NO_CONTENT, {})

    def do_GET(self) -> None:
        if self.path == "/health":
            self._send_json(HTTPStatus.OK, {"status": "ok"})
            return

        user = self._require_user()
        if not user:
            return

        if self.path == "/bootstrap":
            self._send_json(HTTPStatus.OK, self.context.store.snapshot_for(user["id"]))
        elif self.path == "/profile":
            self._send_json(HTTPStatus.OK, {"user": user})
        elif self.path == "/activities":
            self._send_json(HTTPStatus.OK, {"activities": self.context.store.snapshot_for(user["id"])["activities"]})
        elif self.path == "/challenges":
            self._send_json(HTTPStatus.OK, {"challenges": self.context.store.snapshot_for(user["id"])["challenges"]})
        elif self.path == "/posts":
            self._send_json(HTTPStatus.OK, {"posts": self.context.store.snapshot_for(user["id"])["posts"]})
        elif self.path == "/chat/messages":
            self._send_json(HTTPStatus.OK, {"messages": self.context.store.snapshot_for(user["id"])["chatMessages"]})
        else:
            self._send_error_json(HTTPStatus.NOT_FOUND, "Route not found.")

    def do_POST(self) -> None:
        payload = self._read_json()
        if payload is None:
            return

        if self.path == "/auth/register":
            if not self._require_fields(payload, ["fullName", "email", "password"]):
                return
            try:
                token, user = self.context.store.register(payload["fullName"], payload["email"], payload["password"])
            except ValueError as error:
                self._send_error_json(HTTPStatus.CONFLICT, str(error))
                return
            self._send_json(HTTPStatus.CREATED, {"token": token, "user": user})
            return

        if self.path == "/auth/login":
            if not self._require_fields(payload, ["email", "password"]):
                return
            try:
                token, user = self.context.store.login(payload["email"], payload["password"])
            except ValueError as error:
                self._send_error_json(HTTPStatus.UNAUTHORIZED, str(error))
                return
            self._send_json(HTTPStatus.OK, {"token": token, "user": user})
            return

        user = self._require_user()
        if not user:
            return

        if self.path == "/activities":
            if not self._require_fields(payload, ["category", "title", "co2Saved", "points"]):
                return
            result = self.context.store.add_activity(
                user["id"],
                str(payload["category"]),
                str(payload["title"]),
                float(payload["co2Saved"]),
                int(payload["points"]),
                str(payload.get("note", "")),
                list(payload.get("media", [])),
                bool(payload.get("shareToNews", True)),
            )
            self._send_json(HTTPStatus.CREATED, result)
        elif self.path == "/posts":
            try:
                post = self.context.store.add_post(user["id"], str(payload.get("text", "")), list(payload.get("media", [])))
            except ValueError as error:
                self._send_error_json(HTTPStatus.BAD_REQUEST, str(error))
                return
            self._send_json(HTTPStatus.CREATED, {"post": post})
        elif self.path == "/chat/messages":
            try:
                messages = self.context.store.add_chat_message(user["id"], str(payload.get("text", "")))
            except ValueError as error:
                self._send_error_json(HTTPStatus.BAD_REQUEST, str(error))
                return
            self._send_json(HTTPStatus.CREATED, {"messages": messages})
        else:
            self._send_error_json(HTTPStatus.NOT_FOUND, "Route not found.")

    @property
    def context(self) -> AppContext:
        return self.server.context  # type: ignore[attr-defined]

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _require_user(self) -> dict[str, Any] | None:
        auth_header = self.headers.get("Authorization", "")
        token = auth_header.removeprefix("Bearer ").strip() if auth_header.startswith("Bearer ") else None
        user = self.context.store.authenticate(token)
        if not user:
            self._send_error_json(HTTPStatus.UNAUTHORIZED, "Missing or invalid bearer token.")
            return None
        return user

    def _read_json(self) -> dict[str, Any] | None:
        content_length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(content_length) if content_length > 0 else b"{}"
        try:
            return json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._send_error_json(HTTPStatus.BAD_REQUEST, "Malformed JSON payload.")
            return None

    def _require_fields(self, payload: dict[str, Any], fields: list[str]) -> bool:
        missing = [field for field in fields if field not in payload or str(payload[field]).strip() == ""]
        if missing:
            self._send_error_json(HTTPStatus.BAD_REQUEST, f"Missing required fields: {', '.join(missing)}")
            return False
        return True

    def _send_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status.value)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _send_error_json(self, status: HTTPStatus, message: str) -> None:
        self._send_json(status, {"error": message})


def create_server(host: str, port: int, db_reference: str | Path | None = None) -> ThreadingHTTPServer:
    if isinstance(db_reference, Path):
        database_url = db_reference.read_text(encoding="utf-8").strip()
    elif db_reference:
        database_url = str(db_reference)
    else:
        database_url = os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)
    store = PostgresStore(database_url)
    server = ThreadingHTTPServer((host, port), EcoRequestHandler)
    server.context = AppContext(store=store)  # type: ignore[attr-defined]
    return server


def main() -> None:
    parser = argparse.ArgumentParser(description="EcoIZ backend server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--db-url", default=os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL))
    parser.add_argument("--data", default="", help="Deprecated. Ignored unless it points to a text file containing DATABASE_URL.")
    args = parser.parse_args()

    db_reference: str | Path | None
    if args.data and Path(args.data).exists():
        db_reference = Path(args.data)
    else:
        db_reference = args.db_url

    server = create_server(args.host, args.port, db_reference)
    print(f"EcoIZ backend running on http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
