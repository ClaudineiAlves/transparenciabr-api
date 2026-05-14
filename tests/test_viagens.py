import re

import pytest
from pytest_httpx import HTTPXMock

VIAGEM_FIXTURE = {
    "id": 1,
    "viagem": {
        "motivo": "Reunião de trabalho",
        "pcdp": "0000000000000000001",
        "ano": 2025,
        "numPcdp": "000001/25",
        "justificativaUrgente": None,
        "urgenciaViagem": "Não",
    },
    "situacao": "Realizada",
    "beneficiario": {
        "cpfFormatado": "***.000.000-**",
        "nis": "",
        "nome": "SERVIDOR TESTE",
    },
    "cargo": {"codigoSIAPE": "000000", "descricao": "Analista"},
    "funcao": {"codigoSIAPE": "-1", "descricao": "Sem informação"},
    "tipoViagem": "Nacional",
    "orgao": {
        "nome": "Ministério Teste",
        "codigoSIAFI": "26000",
        "cnpj": "00000000000000",
        "sigla": "MEC",
        "descricaoPoder": "EXECUTIVO",
    },
    "dataInicioAfastamento": "2025-01-10",
    "dataFimAfastamento": "2025-01-12",
    "valorTotalDiarias": 500.0,
    "valorTotalPassagem": 1200.0,
    "valorTotalViagem": 1700.0,
    "valorTotalDevolucao": 0.0,
    "valorTotalRestituicao": 0.0,
    "valorMulta": 0.0,
    "valorTotalTaxaAgenciamento": 0.0,
}


@pytest.mark.asyncio
async def test_listar_viagens_retorna_pagina(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(url=re.compile(r".*/viagens.*"), json=[VIAGEM_FIXTURE])

    response = await client.get(
        "/v1/viagens",
        params={
            "codigo_orgao": "26000",
            "data_ida_de": "01/01/2025",
            "data_ida_ate": "31/01/2025",
            "data_retorno_de": "01/01/2025",
            "data_retorno_ate": "31/01/2025",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["pagina"] == 1
    assert len(body["itens"]) == 1
    assert body["itens"][0]["id"] == 1
    assert body["itens"][0]["valorTotalViagem"] == 1700.0


@pytest.mark.asyncio
async def test_listar_viagens_portal_indisponivel(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(url=re.compile(r".*/viagens.*"), status_code=503)

    response = await client.get(
        "/v1/viagens",
        params={
            "codigo_orgao": "26000",
            "data_ida_de": "01/01/2025",
            "data_ida_ate": "31/01/2025",
            "data_retorno_de": "01/01/2025",
            "data_retorno_ate": "31/01/2025",
        },
    )

    assert response.status_code == 502
