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
        Base.metadata.create_all(cls.engine)
        with cls.SessionLocal() as db:
            ensure_seed_data(db)

        def override_get_db():
            db = cls.SessionLocal()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        cls.client = TestClient(app)

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
        self.assertGreaterEqual(len(achievements.json()), 3)

        posts = self.client.get(
            "/admin/posts",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(posts.status_code, 200)
        self.assertGreaterEqual(len(posts.json()), 2)

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


if __name__ == "__main__":
    unittest.main()
