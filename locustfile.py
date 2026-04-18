from locust import HttpUser, task, between


# ─────────────────────────────────────────────
#  ANONYMOUS USER
# ─────────────────────────────────────────────
class AnonymousUser(HttpUser):
    wait_time = between(1, 3)
    weight = 5

    @task(5)
    def view_home(self):
        self.client.get("/")

    @task(2)
    def view_login_page(self):
        self.client.get("/login/")

    @task(2)
    def view_register_page(self):
        self.client.get("/register/")

    @task(1)
    def view_profile(self):
        self.client.get("/profile/locustuser/")


# ─────────────────────────────────────────────
#  LOGGED IN USER
# ─────────────────────────────────────────────
class LoggedInUser(HttpUser):
    wait_time = between(2, 5)
    weight = 2

    def on_start(self):
        response = self.client.get("/login/")
        csrf_token = response.cookies.get("csrftoken")
        self.client.post("/login/", {
            "username": "locustuser",
            "password": "Testpass@123",
            "csrfmiddlewaretoken": csrf_token,
        }, headers={"Referer": "http://127.0.0.1:8000/login/"})

    @task(3)
    def view_dashboard(self):
        self.client.get("/dashboard/")

    @task(2)
    def view_review_queue(self):
        self.client.get("/review/")

    @task(2)
    def view_upload_page(self):
        self.client.get("/upload/")

    @task(1)
    def view_profile(self):
        self.client.get("/profile/locustuser/")

    @task(1)
    def view_home(self):
        self.client.get("/")


# ─────────────────────────────────────────────
#  STRESS USER
# ─────────────────────────────────────────────
class StressUser(HttpUser):
    wait_time = between(0.1, 0.5)
    weight = 1

    @task
    def rapid_home(self):
        self.client.get("/")

    @task
    def rapid_login_page(self):
        self.client.get("/login/")
