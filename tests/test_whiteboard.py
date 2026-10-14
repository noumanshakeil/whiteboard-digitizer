import pytest

@pytest.mark.asyncio
async def test_export_blocks(client):
    c = await client.post("/api/captures", json={"title": "Standup", "hint_text": "Goal A. Goal B. Owner: team."})
    cid = c.json()["id"]
    ex = await client.get(f"/api/captures/{cid}/export")
    assert ex.status_code == 200
    data = ex.json()
    assert data["blocks"]
    assert "Whiteboard notes" in data["markdown"]
