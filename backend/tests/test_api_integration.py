def _register(client, email="test@example.com", org="Test Org"):
    return client.post(
        "/api/v1/auth/register",
        json={
            "organization_name": org,
            "industry": "Technology",
            "email": email,
            "password": "SecurePass1!",
        },
    )


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_register_create_activity_summary(client):
    reg = _register(client)
    assert reg.status_code == 201
    token = reg.json()["access_token"]

    factors = client.get("/api/v1/factors", headers=_auth_headers(token))
    assert factors.status_code == 200
    electricity = next(f for f in factors.json() if f["category"] == "electricity" and f["region"] == "UK")
    factor_id = electricity["id"]

    created = client.post(
        "/api/v1/activities",
        headers=_auth_headers(token),
        json={
            "emission_factor_id": factor_id,
            "description": "Office electricity January",
            "quantity": 1000,
            "unit": "kWh",
            "period_start": "2026-01-01T00:00:00",
            "period_end": "2026-01-31T00:00:00",
        },
    )
    assert created.status_code == 201
    body = created.json()
    assert body["emission"]["co2e_kg"] == 207.0

    summary = client.get("/api/v1/emissions/summary?year=2026", headers=_auth_headers(token))
    assert summary.status_code == 200
    data = summary.json()
    assert data["total_co2e_kg"] == 207.0
    assert len(data["by_scope"]) == 3


def test_update_activity_recalculates(client):
    reg = _register(client, email="update@example.com")
    token = reg.json()["access_token"]
    headers = _auth_headers(token)

    factor = next(
        f
        for f in client.get("/api/v1/factors", headers=headers).json()
        if f["category"] == "electricity" and f["region"] == "UK"
    )

    created = client.post(
        "/api/v1/activities",
        headers=headers,
        json={
            "emission_factor_id": factor["id"],
            "description": "HQ power",
            "quantity": 100,
            "unit": "kWh",
            "period_start": "2026-02-01T00:00:00",
            "period_end": "2026-02-28T00:00:00",
        },
    )
    activity_id = created.json()["entry"]["id"]

    updated = client.put(
        f"/api/v1/activities/{activity_id}",
        headers=headers,
        json={"quantity": 200},
    )
    assert updated.status_code == 200
    assert updated.json()["emission"]["co2e_kg"] == 41.4


def test_audit_log_admin_only(client):
    reg = _register(client, email="admin@example.com")
    token = reg.json()["access_token"]
    headers = _auth_headers(token)

    audit = client.get("/api/v1/audit-log", headers=headers)
    assert audit.status_code == 200
    entries = audit.json()
    assert len(entries) >= 1
    assert any(e["entity_type"] == "organization" for e in entries)
