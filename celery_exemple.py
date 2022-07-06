import requests

task = requests.post('http://127.0.0.1:5000/celery/', json={'submit': 'Send'})
task_id = task['task_id']
print(task_id)