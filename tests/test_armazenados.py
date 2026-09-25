import datetime as dt
from decimal import Decimal

import pytest

from app.core import database
from app.models import Contrato, Licitacao, Viagem
from app.repositories import registros


def _contrato(id_: int, orgao: str, assinatura: dt.date, valor: str) -> dict:
    return {
        "id": id_,
        "numero": f"{id_}/2025",
        "objeto": "Serviços de TI",
        "situacao": "Vigente",
        "modalidade": "Pregão Eletrônico",
        "fornecedor_cnpj": "00.000.000/0001-00",
        "fornecedor_nome": "EMPRESA LTDA",
        "unidade_gestora_codigo": "150002",
        "orgao_codigo": orgao,
        "data_assinatura": assinatura,
        "data_inicio_vigencia": assinatura,
        "data_fim_vigencia": None,
        "valor_inicial": Decimal(valor),
        "valor_final": Decimal(valor),
    }


@pytest.fixture
async def contratos_gravados(banco):
    async with banco() as session:
        await registros.salvar(
            session,
            Contrato,
            [
                _contrato(1, "26000", dt.date(2025, 1, 10), "5000.00"),
                _contrato(2, "26000", dt.date(2025, 1, 20), "250000.00"),
                _contrato(3, "26000", dt.date(2025, 3, 5), "90000.00"),
                _contrato(4, "36000", dt.date(2025, 1, 15), "120000.00"),
            ],
        )


async def test_filtra_por_orgao_periodo_e_valor(client, contratos_gravados):
    response = await client.get(
        "/v1/contratos/armazenados",
        params={
            "codigo_orgao": "26000",
            "data_de": "2025-01-01",
            "data_ate": "2025-01-31",
            "valor_min": "10000",
        },
    )

    assert response.status_code == 200
    corpo = response.json()
    assert corpo["total"] == 1
    assert [c["id"] for c in corpo["itens"]] == [2]
    assert corpo["itens"][0]["valor_final"] == 250000.0
    assert corpo["itens"][0]["data_assinatura"] == "2025-01-20"


async def test_ordena_do_mais_recente_e_pagina(client, contratos_gravados):
    response = await client.get(
        "/v1/contratos/armazenados", params={"tamanho": 2, "pagina": 2}
    )

    corpo = response.json()
    assert corpo["total"] == 4
    assert (corpo["pagina"], corpo["tamanho"]) == (2, 2)
    # ordem: 05/03 (3), 20/01 (2), 15/01 (4), 10/01 (1)
    assert [c["id"] for c in corpo["itens"]] == [4, 1]


async def test_licitacoes_e_viagens_tambem_sao_consultaveis(client, banco):
    async with banco() as session:
        await registros.salvar(
            session,
            Licitacao,
            [
                {
                    "id": 7,
                    "situacao": "Homologada",
                    "modalidade": "Pregão",
                    "instrumento_legal": None,
                    "valor": Decimal("50000.00"),
                    "unidade_gestora_codigo": "150002",
                    "orgao_codigo": "26000",
                    "data_abertura": dt.date(2025, 1, 10),
                    "data_publicacao": None,
                }
            ],
        )
        await registros.salvar(
            session,
            Viagem,
            [
                {
                    "id": 8,
                    "pcdp": "000123/25",
                    "situacao": "Realizada",
                    "tipo_viagem": "Nacional",
                    "beneficiario_nome": "SERVIDOR",
                    "orgao_codigo": "26000",
                    "data_inicio_afastamento": dt.date(2025, 1, 10),
                    "data_fim_afastamento": dt.date(2025, 1, 12),
                    "valor_total_diarias": Decimal("500.00"),
                    "valor_total_passagem": Decimal("1200.00"),
                    "valor_total_viagem": Decimal("1700.00"),
                }
            ],
        )

    licitacoes = await client.get(
        "/v1/licitacoes/armazenados", params={"valor_max": "60000"}
    )
    viagens = await client.get(
        "/v1/viagens/armazenados", params={"data_de": "2025-01-10"}
    )
    cartoes = await client.get("/v1/cartoes/armazenados")

    assert [i["id"] for i in licitacoes.json()["itens"]] == [7]
    assert viagens.json()["itens"][0]["valor_total_viagem"] == 1700.0
    assert cartoes.json() == {"pagina": 1, "tamanho": 50, "total": 0, "itens": []}


@pytest.mark.parametrize(
    "params",
    [
        {"data_de": "2025-02-01", "data_ate": "2025-01-01"},
        {"valor_min": "500", "valor_max": "100"},
        {"tamanho": 1000},
        {"data_de": "10/01/2025"},
    ],
)
async def test_filtros_invalidos_devolvem_422(client, params):
    response = await client.get("/v1/contratos/armazenados", params=params)

    assert response.status_code == 422


async def test_sem_banco_configurado_devolve_503(client, monkeypatch):
    monkeypatch.setattr(database, "AsyncSessionLocal", None)

    response = await client.get("/v1/viagens/armazenados")

    assert response.status_code == 503
    assert "DATABASE_URL" in response.json()["mensagem"]


async def test_banco_fora_na_consulta_devolve_503(client, banco, monkeypatch):
    async def consulta_quebrada(*args, **kwargs):
        raise OSError("conexão recusada")

    monkeypatch.setattr(registros, "consultar", consulta_quebrada)

    response = await client.get("/v1/cartoes/armazenados")

    assert response.status_code == 503
    assert "conexão recusada" in response.json()["mensagem"]
