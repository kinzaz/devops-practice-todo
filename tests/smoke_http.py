import json
import time
import uuid
from urllib.error import URLError
from urllib.request import Request, urlopen

BASE = 'http://127.0.0.1:8000'


def request(method, path, payload=None):
    body = json.dumps(payload).encode() if payload is not None else None
    req = Request(
        BASE + path,
        data=body,
        method=method,
        headers={'Content-Type': 'application/json'},
    )
    with urlopen(req, timeout=2) as response:
        content = response.read()
        return response.status, json.loads(content) if content else None


# Даём приложению время запуститься.
for attempt in range(30):
    try:
        status, health = request('GET', '/api/health')
        assert status == 200 and health == {'status': 'ok'}
        break
    except URLError:
        time.sleep(0.2)
else:
    raise RuntimeError('API не стал доступен')


title = 'Docker smoke ' + uuid.uuid4().hex[:8]

status, todo = request('POST', '/api/todos', {'title': title})
assert status == 201, (status, todo)
assert todo['title'] == title
assert todo['done'] is False
todo_id = todo['id']

status, todos = request('GET', '/api/todos')
assert status == 200
assert any(item['id'] == todo_id for item in todos)

status, updated = request(
    'PATCH', f'/api/todos/{todo_id}', {'done': True}
)
assert status == 200
assert updated['done'] is True

status, _ = request('DELETE', f'/api/todos/{todo_id}')
assert status == 204

_, todos = request('GET', '/api/todos')
assert all(item['id'] != todo_id for item in todos)

print('Smoke test passed: health, create, list, update, delete')