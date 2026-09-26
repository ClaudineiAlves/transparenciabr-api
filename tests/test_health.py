import pytest


async def test_health_responde_ok(client):
    resposta = await client.get("/health")

    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}


@pytest.mark.parametrize("metodo", ["GET", "HEAD"])
async def test_health_aceita_get_e_head(client, metodo):
    resposta = await client.request(metodo, "/health")

    assert resposta.status_code == 200
