import re

import pytest
from pytest_httpx import HTTPXMock

GASTO_FIXTURE = {
    "id": 1,
    "mesExtrato": "01/2025",
    "dataTransacao": "15/01/2025",
    "valorTransacao": "150,00",
    "tipoCartao": {
        "id": 1,
        "codigo": "1",
        "descricao": "Cartão de Pagamento do Governo Federal",
    },
    "estabelecimento": {
        "id": 10,
        "cnpjFormatado": "00.000.000/0001-00",
        "cpfFormatado": "",
        "nome": "EMPRESA TESTE",
        "razaoSocialReceita": "EMPRESA TESTE LTDA",
        "nomeFantasiaReceita": "EMPRESA TESTE",
        "tipo": "Entidades Empresariais Privadas",
    },
    "unidadeGestora": {
        "codigo": "100001",
        "nome": "UNIDADE TESTE",
        "descricaoPoder": "EXECUTIVO",
        "orgaoVinculado": {
            "codigoSIAFI": "26000",
            "cnpj": "00000000000000",
            "sigla": "MEC",
            "nome": "Ministério da Educação",
        },
        "orgaoMaximo": {
            "codigo": "26000",
            "sigla": "MEC",
            "nome": "Ministério da Educação",
        },
    },
    "portador": {"cpfFormatado": "***.***.***-**", "nis": "", "nome": "SERVIDOR TESTE"},
}


@pytest.mark.asyncio
async def test_listar_gastos_retorna_pagina(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url=re.compile(r".*/cartoes.*"),
        json=[GASTO_FIXTURE],
    )

    response = await client.get(
        "/v1/cartoes",
        params={
            "mes_ano_inicio": "01/2025",
            "mes_ano_fim": "01/2025",
            "codigo_orgao": "26000",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["pagina"] == 1
    assert len(body["itens"]) == 1
    assert body["itens"][0]["id"] == 1


@pytest.mark.asyncio
async def test_listar_gastos_pagina_parametro(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(url=re.compile(r".*/cartoes.*"), json=[GASTO_FIXTURE])

    response = await client.get(
        "/v1/cartoes",
        params={
            "mes_ano_inicio": "01/2025",
            "mes_ano_fim": "01/2025",
            "codigo_orgao": "26000",
            "pagina": 3,
        },
    )

    assert response.status_code == 200
    assert response.json()["pagina"] == 3


@pytest.mark.asyncio
async def test_listar_gastos_portal_indisponivel(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(url=re.compile(r".*/cartoes.*"), status_code=503)

    response = await client.get(
        "/v1/cartoes",
        params={
            "mes_ano_inicio": "01/2025",
            "mes_ano_fim": "01/2025",
            "codigo_orgao": "26000",
        },
    )

    assert response.status_code == 502
    assert "mensagem" in response.json()


@pytest.mark.asyncio
async def test_listar_gastos_sem_filtros_obrigatorios(client):
    response = await client.get(
        "/v1/cartoes",
        params={"mes_ano_inicio": "01/2025"},
    )

    assert response.status_code == 422
