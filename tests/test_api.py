from fastapi.testclient import TestClient
from backend.app.main import app


def test_game_flow():
    client = TestClient(app)

    r = client.post('/api/games', json={'human_name': '你', 'mode': 'quick'})
    assert r.status_code == 200
    game = r.json()
    gid = game['game_id']
    assert len(game['players']) == 6

    r = client.post(f'/api/games/{gid}/speeches')
    assert r.status_code == 200
    assert r.json()['phase'] == 'voting'

    target = next(p['player_id'] for p in game['players'] if p['player_id'] != 'p1')
    r = client.post(f'/api/games/{gid}/vote', json={'target_player_id': target})
    assert r.status_code == 200
    assert r.json()['phase'] in ['day', 'conclusion']

    r = client.post(f'/api/games/{gid}/llm/switch', json={'mode': 'local', 'provider': 'ollama'})
    assert r.status_code == 200
    assert r.json()['llm_config']['mode'] == 'local'
