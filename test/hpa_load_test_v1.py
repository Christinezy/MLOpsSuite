import requests
from datetime import datetime

project_id = 1


counter = 0


while True:
    requests.get(
        url = f"http://localhost/project{project_id}/test"
    )

    counter += 1

    if counter == 50:
        print(f"{datetime.now()} - [INFO] Sent 50 requests")
        counter = 0 
