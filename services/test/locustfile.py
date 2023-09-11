import requests
from datetime import datetime
from locust import HttpUser, task

project_id = 1

class HelloWorldUser(HttpUser):
    @task
    def load_test_model_deployment(self):
        self.client.get(f"http://localhost/project{project_id}/test")




# counter = 0


# while True:
#     requests.get(
#         url = f"http://localhost/project{project_id}/test"
#     )

#     counter += 1

#     if counter == 50:
#         print(f"{datetime.now()} - [INFO] Sent 50 requests")
#         counter = 0 
