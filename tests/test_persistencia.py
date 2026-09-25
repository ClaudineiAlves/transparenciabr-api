import datetime as dt
import logging
import re
from decimal import Decimal

from pytest_httpx import HTTPXMock
from sqlalchemy import func, select

from app.core import database
from app.models import Cartao, Contrato
from app.repositories import registros
from app.schemas.cartoes import GastoCartao
from app.services import normalizacao
from tests.test_cartoes import GASTO_FIXTURE
from tests.test_contratos import CONTRATO_FIXTURE

PARAMS_CONTRATOS = {
    "codigo_orgao": "26000",
    "data_inicio_de": "01/01/2025",
    "data_inicio_ate": "31/01/2025",
}
PARAMS_CARTOES = {
    "mes_ano_inicio": "01/2025",
    "mes_ano_fim": "01/2025",
    "codigo_orgao": "26000",
}


async def test_pagina_do_portal_e_gravada_normalizada(
    client, banco, httpx_mock: HTTPXMock
):
    httpx_mock.add_response(url=re.compile(r".*/contratos.*"), json=[CONTRATO_FIXTURE])

    response = await client.get("/v1/contratos", params=PARAMS_CONTRATOS)

    assert response.status_code == 200
    async with banco() as session:
        contrato = await session.get(Contrato, 1)
    assert contrato.data_assinatura == dt.date(2025, 1, 15)
    assert contrato.valor_final == Decimal("100000.00")
    assert contrato.orgao_codigo == "26000"
    assert contrato.atualizado_em is not None


async def test_consultar_de_novo_atualiza_sem_duplicar(
    client, banco, httpx_mock: HTTPXMock
):
    corrigido = {**CONTRATO_FIXTURE, "valorFinalCompra": 120000.0}
    httpx_mock.add_response(url=re.compile(r".*/contratos.*"), json=[CONTRATO_FIXTURE])
    httpx_mock.add_response(url=re.compile(r".*/contratos.*"), json=[corrigido])

    await client.get("/v1/contratos", params=PARAMS_CONTRATOS)
    await client.get("/v1/contratos", params=PARAMS_CONTRATOS)

    async with banco() as session:
        total = await session.scalar(select(func.count()).select_from(Contrato))
        contrato = await session.get(Contrato, 1)
    assert total == 1
    assert contrato.valor_final == Decimal("120000.00")


async def test_valor_em_texto_brasileiro_vira_numero(
    client, banco, httpx_mock: HTTPXMock
):
    gasto = {**GASTO_FIXTURE, "valorTransacao": "1.234,56"}
    httpx_mock.add_response(url=re.compile(r".*/cartoes.*"), json=[gasto])

    await client.get("/v1/cartoes", params=PARAMS_CARTOES)

    async with banco() as session:
        cartao = await session.get(Cartao, 1)
    assert cartao.valor_transacao == Decimal("1234.56")
    assert cartao.data_transacao == dt.date(2025, 1, 15)


async def test_texto_maior_que_a_coluna_e_cortado(banco):
    gasto = {**GASTO_FIXTURE, "estabelecimento": {**GASTO_FIXTURE["estabelecimento"]}}
    gasto["estabelecimento"]["nome"] = "X" * 1000

    registro = normalizacao.cartao(GastoCartao(**gasto))

    async with banco() as session:
        await registros.salvar(session, Cartao, [registro])
        cartao = await session.get(Cartao, 1)
    assert len(cartao.estabelecimento_nome) == 300


async def test_banco_fora_nao_derruba_a_consulta_ao_portal(
    client, httpx_mock: HTTPXMock, monkeypatch, caplog
):
    def sessao_quebrada():
        raise OSError("conexão recusada")

    monkeypatch.setattr(database, "AsyncSessionLocal", sessao_quebrada)
    httpx_mock.add_response(url=re.compile(r".*/cartoes.*"), json=[GASTO_FIXTURE])

    with caplog.at_level(logging.WARNING):
        response = await client.get("/v1/cartoes", params=PARAMS_CARTOES)

    assert response.status_code == 200
    assert response.json()["itens"][0]["id"] == 1
    assert "Não foi possível gravar 1 registros em cartoes" in caplog.text


async def test_sem_banco_configurado_a_api_so_nao_grava(
    client, httpx_mock: HTTPXMock, monkeypatch
):
    monkeypatch.setattr(database, "AsyncSessionLocal", None)
    httpx_mock.add_response(url=re.compile(r".*/cartoes.*"), json=[GASTO_FIXTURE])

    response = await client.get("/v1/cartoes", params=PARAMS_CARTOES)

    assert response.status_code == 200


async def test_pagina_vazia_nao_toca_no_banco(banco):
    async with banco() as session:
        assert await registros.salvar(session, Cartao, []) == 0
