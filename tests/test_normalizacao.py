import datetime as dt
from decimal import Decimal

import pytest

from app.schemas.cartoes import GastoCartao
from app.schemas.contratos import Contrato
from app.schemas.licitacoes import Licitacao
from app.schemas.viagens import Viagem
from app.services import normalizacao
from app.services.normalizacao import para_data, para_decimal
from tests.test_cartoes import GASTO_FIXTURE
from tests.test_contratos import CONTRATO_FIXTURE
from tests.test_licitacoes import LICITACAO_FIXTURE
from tests.test_viagens import VIAGEM_FIXTURE


@pytest.mark.parametrize(
    ("texto", "esperado"),
    [
        ("15/01/2025", dt.date(2025, 1, 15)),
        ("2025-01-15", dt.date(2025, 1, 15)),
        (" 03/02/2025 ", dt.date(2025, 2, 3)),
        ("31/02/2025", None),
        ("sigiloso", None),
        ("", None),
        (None, None),
    ],
)
def test_para_data(texto, esperado):
    assert para_data(texto) == esperado


@pytest.mark.parametrize(
    ("valor", "esperado"),
    [
        ("150,00", Decimal("150.00")),
        ("1.234,56", Decimal("1234.56")),
        ("150.5", Decimal("150.50")),
        (100000.0, Decimal("100000.00")),
        (0.1 + 0.2, Decimal("0.30")),
        ("abc", None),
        ("", None),
        (None, None),
        (float("nan"), None),
    ],
)
def test_para_decimal(valor, esperado):
    assert para_decimal(valor) == esperado


def test_cartao_normaliza_data_e_valor_em_texto():
    registro = normalizacao.cartao(GastoCartao(**GASTO_FIXTURE))

    assert registro["data_transacao"] == dt.date(2025, 1, 15)
    assert registro["valor_transacao"] == Decimal("150.00")
    assert registro["orgao_codigo"] == "26000"
    assert registro["portador_nome"] == "SERVIDOR TESTE"


def test_contrato_licitacao_e_viagem_viram_colunas_do_banco():
    contrato = normalizacao.contrato(Contrato(**CONTRATO_FIXTURE))
    licitacao = normalizacao.licitacao(Licitacao(**LICITACAO_FIXTURE))
    viagem = normalizacao.viagem(Viagem(**VIAGEM_FIXTURE))

    assert contrato["data_assinatura"] == dt.date(2025, 1, 15)
    assert contrato["valor_final"] == Decimal("100000.00")
    assert licitacao["data_abertura"] == dt.date(2025, 1, 10)
    assert licitacao["valor"] == Decimal("50000.00")
    assert viagem["data_inicio_afastamento"] == dt.date(2025, 1, 10)
    assert viagem["valor_total_viagem"] == Decimal("1700.00")
