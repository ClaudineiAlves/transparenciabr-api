import re

import pytest
from pytest_httpx import HTTPXMock

CONTRATO_FIXTURE = {
    "id": 1,
    "numero": "001/2025",
    "objeto": "Prestação de serviços de TI",
    "numeroProcesso": "00000.000001/2025-01",
    "fundamentoLegal": "Lei nº 14.133/2021",
    "compra": {
        "numero": "00001/2025",
        "objeto": "Serviços de TI",
        "numeroProcesso": "00000.000001/2025-01",
        "contatoResponsavel": "SERVIDOR RESPONSAVEL",
    },
    "situacaoContrato": "Vigente",
    "modalidadeCompra": "Pregão Eletrônico",
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
    "dataAssinatura": "2025-01-15",
    "dataPublicacaoDOU": "2025-01-20",
    "dataInicioVigencia": "2025-01-15",
    "dataFimVigencia": "2026-01-15",
    "fornecedor": {
        "id": 1,
        "cpfFormatado": "",
        "cnpjFormatado": "00.000.000/0001-00",
        "nome": "EMPRESA FORNECEDORA LTDA",
        "razaoSocialReceita": "EMPRESA FORNECEDORA LTDA",
        "nomeFantasiaReceita": "FORNECEDORA",
        "tipo": "Entidades Empresariais Privadas",
    },
    "valorInicialCompra": 100000.0,
    "valorFinalCompra": 100000.0,
}


@pytest.mark.asyncio
async def test_listar_contratos_retorna_pagina(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(url=re.compile(r".*/contratos.*"), json=[CONTRATO_FIXTURE])

    response = await client.get(
        "/v1/contratos",
        params={
            "codigo_orgao": "26000",
            "data_inicio_de": "01/01/2025",
            "data_inicio_ate": "31/01/2025",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["pagina"] == 1
    assert len(body["itens"]) == 1
    assert body["itens"][0]["valorFinalCompra"] == 100000.0


@pytest.mark.asyncio
async def test_listar_contratos_portal_indisponivel(client, httpx_mock: HTTPXMock):
    httpx_mock.add_response(url=re.compile(r".*/contratos.*"), status_code=503)

    response = await client.get(
        "/v1/contratos",
        params={
            "codigo_orgao": "26000",
            "data_inicio_de": "01/01/2025",
            "data_inicio_ate": "31/01/2025",
        },
    )

    assert response.status_code == 502
