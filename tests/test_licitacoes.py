import re

import pytest
from pytest_httpx import HTTPXMock

LICITACAO_FIXTURE = {
    "id": 1,
    "licitacao": {
        "numero": "001/2025",
        "objeto": "Aquisição de equipamentos",
        "numeroProcesso": "00000.000001/2025-01",
        "contatoResponsavel": "SERVIDOR RESPONSAVEL",
    },
    "dataAbertura": "2025-01-10",
    "dataPublicacao": "2025-01-05",
    "situacaoCompra": "Homologada",
    "modalidadeLicitacao": "Pregão Eletrônico",
    "instrumentoLegal": "Lei nº 14.133/2021",
    "valor": 50000.0,
    "municipio": {
        "codigoIBGE": "5300108",
        "nomeIBGE": "Brasília",
        "pais": "Brasil",
        "uf": {"sigla": "DF", "nome": "Distrito Federal"},
    },
    "unidadeGestora": {
        "codigo": "150002",
        "nome": "UNIDADE GESTORA TESTE",
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
}


@pytest.mark.asyncio
async def test_listar_licitacoes_retorna_pagina(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url=re.compile(r".*/licitacoes.*"), json=[LICITACAO_FIXTURE]
    )

    response = await client.get(
        "/v1/licitacoes",
        params={
            "codigo_orgao": "26000",
            "data_inicial": "01/01/2025",
            "data_final": "31/01/2025",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["pagina"] == 1
    assert len(body["itens"]) == 1
    assert body["itens"][0]["valor"] == 50000.0


@pytest.mark.asyncio
async def test_listar_licitacoes_portal_indisponivel(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(url=re.compile(r".*/licitacoes.*"), status_code=503)

    response = await client.get(
        "/v1/licitacoes",
        params={
            "codigo_orgao": "26000",
            "data_inicial": "01/01/2025",
            "data_final": "31/01/2025",
        },
    )

    assert response.status_code == 502


@pytest.mark.asyncio
async def test_listar_licitacoes_parametros_invalidos(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url=re.compile(r".*/licitacoes.*"),
        status_code=400,
        json={"mensagem": "Período máximo permitido é de 1 mês"},
    )

    response = await client.get(
        "/v1/licitacoes",
        params={
            "codigo_orgao": "26000",
            "data_inicial": "01/01/2025",
            "data_final": "31/12/2025",
        },
    )

    assert response.status_code == 422
    assert "mensagem" in response.json()
