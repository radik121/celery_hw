import time

import requests

task = requests.post('http://127.0.0.1:5000/celery/', json={'submit': 'Send'}).json()
task_id = task['task_id']

while True:
    result = requests.get(f"http://127.0.0.1:5000/celery/{task_id}").json()
    print(result)
    if result['status'] != "PENDING":
        break
    time.sleep(0.1)