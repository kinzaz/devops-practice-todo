from fastapi.testclient import TestClient
from app import main


def test_todo_lifecycle_and_persistence(tmp_path, monkeypatch):
    monkeypatch.setattr(main, 'DATABASE', tmp_path / 'test.db')
    with TestClient(main.app) as client:
        assert client.get('/api/todos').json() == []
        assert client.post('/api/todos', json={'title': '  '}).status_code == 422
        response = client.post('/api/todos', json={'title': ' Первая задача '})
        assert response.status_code == 201
        todo = response.json()
        assert todo['title'] == 'Первая задача'
        assert todo['done'] is False
        assert client.patch(f'/api/todos/{todo["id"]}', json={'done': True}).json()['done'] is True
    with TestClient(main.app) as client:
        assert client.get('/api/todos').json()[0]['done'] is True
        assert client.delete(f'/api/todos/{todo["id"]}').status_code == 204
        assert client.delete(f'/api/todos/{todo["id"]}').status_code == 404
        assert client.patch('/api/todos/999', json={'done': False}).status_code == 404
        assert client.get('/api/todos').json() == []
