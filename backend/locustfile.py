from locust import HttpUser, task, between
import random
import string


def rand_email():
    return "".join(random.choices(string.ascii_lowercase, k=8)) + "@example.com"


class KanbanUser(HttpUser):
    wait_time = between(1, 3)
    token = None
    project_id = None
    board_id = None
    column_id = None

    def on_start(self):
        email = rand_email()
        self.client.post("/auth/register", json={
            "email": email, "password": "password123", "role": "admin"
        })
        r = self.client.post("/auth/login", json={
            "email": email, "password": "password123"
        })
        self.token = r.json()["access_token"]
        self.client.headers.update({"Authorization": f"Bearer {self.token}"})

        p = self.client.post("/projects", json={"name": "Load Project"}).json()
        self.project_id = p["id"]
        b = self.client.post(f"/projects/{self.project_id}/boards", json={"name": "Load Board"}).json()
        self.board_id = b["id"]
        c = self.client.post(f"/boards/{self.board_id}/columns", json={"name": "To Do", "order": 0}).json()
        self.column_id = c["id"]

    @task(5)
    def create_card(self):
        self.client.post(f"/columns/{self.column_id}/cards", json={
            "title": f"Task {random.randint(1, 10000)}",
            "priority": random.choice(["low", "medium", "high", "critical"])
        })

    @task(10)
    def list_cards(self):
        self.client.get(f"/columns/{self.column_id}/cards")

    @task(3)
    def search_cards(self):
        self.client.get("/cards", params={"search": "Task"})

    @task(2)
    def list_projects(self):
        self.client.get("/projects")
