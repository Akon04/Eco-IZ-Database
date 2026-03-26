import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_current_user
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.services.seed import ensure_seed_data


class BackendAPITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.engine = create_engine(
            "sqlite+pysqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            future=True,
        )
        cls.SessionLocal = sessionmaker(bind=cls.engine, autoflush=False, autocommit=False, future=True)

        def override_get_db():
            db = cls.SessionLocal()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        cls.client = TestClient(app)

    def setUp(self) -> None:
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)
        with self.SessionLocal() as db:
            ensure_seed_data(db)

    @classmethod
    def tearDownClass(cls) -> None:
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(get_current_user, None)
        cls.engine.dispose()

    def test_login_bootstrap_and_chat_flow(self) -> None:
        login = self.client.post(
            "/auth/login",
            json={"email": "user@ecoiz.app", "password": "password123"},
        )
        self.assertEqual(login.status_code, 200)
        token = login.json()["token"]

        bootstrap = self.client.get(
            "/bootstrap",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(bootstrap.status_code, 200)
        bootstrap_body = bootstrap.json()
        self.assertEqual(bootstrap_body["user"]["email"], "user@ecoiz.app")
        self.assertGreaterEqual(len(bootstrap_body["activities"]), 2)
        self.assertGreaterEqual(len(bootstrap_body["chatMessages"]), 1)
        self.assertEqual(len(bootstrap_body["challenges"]), 5)

        chat = self.client.post(
            "/chat/messages",
            json={"text": "Как не забывать про воду?"},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(chat.status_code, 201)
        messages = chat.json()["messages"]
        self.assertEqual(len(messages), 2)
        self.assertTrue(messages[0]["isUser"])
        self.assertFalse(messages[1]["isUser"])
        self.assertIn("душ", messages[1]["text"])

    def test_error_responses(self) -> None:
        unauthorized = self.client.get(
            "/bootstrap",
            headers={"Authorization": "Bearer invalid-token"},
        )
        self.assertEqual(unauthorized.status_code, 401)
        self.assertEqual(unauthorized.json()["error"], "Missing or invalid bearer token.")

        login = self.client.post(
            "/auth/login",
            json={"email": "user@ecoiz.app", "password": "password123"},
        )
        token = login.json()["token"]

        empty_message = self.client.post(
            "/chat/messages",
            json={"text": "   "},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(empty_message.status_code, 400)
        self.assertEqual(empty_message.json()["error"], "Message text is required.")

    def test_admin_endpoints(self) -> None:
        login = self.client.post(
            "/admin/login",
            json={"email": "admin@ecoiz.app", "password": "admin123"},
        )
        self.assertEqual(login.status_code, 200)
        token = login.json()["token"]

        me = self.client.get(
            "/admin/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.json()["role"], "ADMIN")

        users = self.client.get(
            "/admin/users?status=ACTIVE",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(users.status_code, 200)
        self.assertGreaterEqual(len(users.json()), 2)

        categories = self.client.get(
            "/admin/categories",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(categories.status_code, 200)
        self.assertGreaterEqual(len(categories.json()), 3)

        category_id = categories.json()[0]["id"]
        category_name = categories.json()[0]["name"]
        updated_category = self.client.patch(
            f"/admin/categories/{category_id}",
            json={
                "name": category_name,
                "description": "Обновленное описание",
                "color": "#000000",
                "icon": "flash",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(updated_category.status_code, 200)
        self.assertEqual(updated_category.json()["icon"], "flash")

        habits = self.client.get(
            "/admin/habits",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(habits.status_code, 200)
        self.assertGreaterEqual(len(habits.json()), 3)

        achievements = self.client.get(
            "/admin/achievements",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(achievements.status_code, 200)
        self.assertGreaterEqual(len(achievements.json()), 15)

        created_category = self.client.post(
            "/admin/categories",
            json={
                "name": "Воздух",
                "description": "Привычки для чистого воздуха",
                "color": "#7BC6CC",
                "icon": "wind",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(created_category.status_code, 201)
        created_category_body = created_category.json()

        created_habit = self.client.post(
            "/admin/habits",
            json={
                "title": "Проветривать комнату осознанно",
                "description": "Короткое и эффективное проветривание",
                "category": "Воздух",
                "points": 6,
                "co2Value": 0.1,
                "waterValue": 0.0,
                "energyValue": 0.0,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(created_habit.status_code, 201)
        created_habit_body = created_habit.json()

        created_achievement = self.client.post(
            "/admin/achievements",
            json={
                "title": "Тестовая ачивка",
                "description": "Проверка создания achievement",
                "icon": "star.fill",
                "targetValue": 2,
                "rewardPoints": 15,
                "badgeTintHex": 4497988,
                "badgeBackgroundHex": 15464671,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(created_achievement.status_code, 201)
        created_achievement_body = created_achievement.json()

        created_post = self.client.post(
            "/admin/posts",
            json={
                "author": "Admin",
                "content": "Пост для проверки admin CRUD",
                "visibility": "PUBLIC",
                "state": "Published",
                "reportsCount": 0,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(created_post.status_code, 201)
        created_post_body = created_post.json()

        posts = self.client.get(
            "/admin/posts",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(posts.status_code, 200)
        self.assertGreaterEqual(len(posts.json()), 2)

        deleted_post = self.client.delete(
            f"/admin/posts/{created_post_body['id']}",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(deleted_post.status_code, 204)

        deleted_achievement = self.client.delete(
            f"/admin/achievements/{created_achievement_body['id']}",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(deleted_achievement.status_code, 204)

        deleted_habit = self.client.delete(
            f"/admin/habits/{created_habit_body['id']}",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(deleted_habit.status_code, 204)

        deleted_category = self.client.delete(
            f"/admin/categories/{created_category_body['id']}",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(deleted_category.status_code, 204)

    def test_claim_completed_challenge(self) -> None:
        login = self.client.post(
            "/auth/login",
            json={"email": "user@ecoiz.app", "password": "password123"},
        )
        self.assertEqual(login.status_code, 200)
        token = login.json()["token"]

        bootstrap = self.client.get(
            "/bootstrap",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(bootstrap.status_code, 200)
        challenge = next(item for item in bootstrap.json()["challenges"] if item["title"] == "7 эко-действий за неделю")

        remaining = challenge["targetCount"] - challenge["currentCount"]
        for index in range(remaining):
            mutation = self.client.post(
                "/activities",
                json={
                    "category": "Вода",
                    "title": f"Test activity {index}",
                    "co2Saved": 0.1,
                    "points": 1,
                    "note": "",
                    "media": [],
                    "shareToNews": False,
                },
                headers={"Authorization": f"Bearer {token}"},
            )
            self.assertEqual(mutation.status_code, 201)

        claim = self.client.post(
            f"/challenges/{challenge['id']}/claim",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(claim.status_code, 200)
        self.assertTrue(claim.json()["challenge"]["isClaimed"])

        second_claim = self.client.post(
            f"/challenges/{challenge['id']}/claim",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(second_claim.status_code, 409)

    def test_unlocks_five_more_challenges_on_level_up(self) -> None:
        login = self.client.post(
            "/auth/login",
            json={"email": "user@ecoiz.app", "password": "password123"},
        )
        self.assertEqual(login.status_code, 200)
        token = login.json()["token"]

        before = self.client.get(
            "/bootstrap",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(before.status_code, 200)
        self.assertEqual(len(before.json()["challenges"]), 5)

        level_up = self.client.post(
            "/activities",
            json={
                "category": "Энергия",
                "title": "Большой апгрейд уровня",
                "co2Saved": 1.0,
                "points": 40,
                "note": "",
                "media": [],
                "shareToNews": False,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(level_up.status_code, 201)
        self.assertEqual(len(level_up.json()["challenges"]), 10)


if __name__ == "__main__":
    unittest.main()
