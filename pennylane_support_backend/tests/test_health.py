def test_health_check(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"PennyLane Support API is up!" in resp.data
