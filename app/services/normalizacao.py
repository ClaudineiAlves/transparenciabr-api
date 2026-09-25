"""Converte os registros do Portal para o schema relacional, com tipos de verdade."""

import datetime as dt
from decimal import Decimal, InvalidOperation

from app.schemas.cartoes import GastoCartao
from app.schemas.contratos import Contrato
from app.schemas.licitacoes import Licitacao
from app.schemas.viagens import Viagem

_FORMATOS_DATA = ("%d/%m/%Y", "%Y-%m-%d")
_CENTAVOS = Decimal("0.01")


def para_data(texto: str | None) -> dt.date | None:
    """Aceita DD/MM/AAAA e AAAA-MM-DD, os dois formatos que o Portal usa."""
    if not texto:
        return None
    for formato in _FORMATOS_DATA:
        try:
            return dt.datetime.strptime(texto.strip(), formato).date()
        except ValueError:
            continue
    return None


def para_decimal(valor: str | float | None) -> Decimal | None:
    """Converte números e textos no formato brasileiro ("1.234,56")."""
    if valor is None:
        return None
    texto = str(valor).strip()
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    try:
        numero = Decimal(texto)
    except InvalidOperation:
        return None
    return numero.quantize(_CENTAVOS) if numero.is_finite() else None


def cartao(item: GastoCartao) -> dict:
    return {
        "id": item.id,
        "mes_extrato": item.mesExtrato,
        "data_transacao": para_data(item.dataTransacao),
        "valor_transacao": para_decimal(item.valorTransacao),
        "tipo_cartao_descricao": item.tipoCartao.descricao,
        "estabelecimento_cnpj": item.estabelecimento.cnpjFormatado,
        "estabelecimento_nome": item.estabelecimento.nome,
        "unidade_gestora_codigo": item.unidadeGestora.codigo,
        "orgao_codigo": item.unidadeGestora.orgaoVinculado.codigoSIAFI,
        "portador_nome": item.portador.nome,
    }


def contrato(item: Contrato) -> dict:
    return {
        "id": item.id,
        "numero": item.numero,
        "objeto": item.objeto,
        "situacao": item.situacaoContrato,
        "modalidade": item.modalidadeCompra,
        "fornecedor_cnpj": item.fornecedor.cnpjFormatado,
        "fornecedor_nome": item.fornecedor.nome,
        "unidade_gestora_codigo": item.unidadeGestora.codigo,
        "orgao_codigo": item.unidadeGestora.orgaoVinculado.codigoSIAFI,
        "data_assinatura": para_data(item.dataAssinatura),
        "data_inicio_vigencia": para_data(item.dataInicioVigencia),
        "data_fim_vigencia": para_data(item.dataFimVigencia),
        "valor_inicial": para_decimal(item.valorInicialCompra),
        "valor_final": para_decimal(item.valorFinalCompra),
    }


def licitacao(item: Licitacao) -> dict:
    return {
        "id": item.id,
        "situacao": item.situacaoCompra,
        "modalidade": item.modalidadeLicitacao,
        "instrumento_legal": item.instrumentoLegal,
        "valor": para_decimal(item.valor),
        "unidade_gestora_codigo": item.unidadeGestora.codigo,
        "orgao_codigo": item.unidadeGestora.orgaoVinculado.codigoSIAFI,
        "data_abertura": para_data(item.dataAbertura),
        "data_publicacao": para_data(item.dataPublicacao),
    }


def viagem(item: Viagem) -> dict:
    return {
        "id": item.id,
        "pcdp": item.viagem.pcdp,
        "situacao": item.situacao,
        "tipo_viagem": item.tipoViagem,
        "beneficiario_nome": item.beneficiario.nome,
        "orgao_codigo": item.orgao.codigoSIAFI,
        "data_inicio_afastamento": para_data(item.dataInicioAfastamento),
        "data_fim_afastamento": para_data(item.dataFimAfastamento),
        "valor_total_diarias": para_decimal(item.valorTotalDiarias),
        "valor_total_passagem": para_decimal(item.valorTotalPassagem),
        "valor_total_viagem": para_decimal(item.valorTotalViagem),
    }
