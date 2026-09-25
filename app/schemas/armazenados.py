import datetime as dt
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class PaginaArmazenada(BaseModel, Generic[T]):
    pagina: int
    tamanho: int
    total: int
    itens: list[T]


class _Registro(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    orgao_codigo: str
    atualizado_em: dt.datetime


class GastoCartaoArmazenado(_Registro):
    unidade_gestora_codigo: str
    mes_extrato: str
    data_transacao: dt.date | None
    valor_transacao: float | None
    tipo_cartao_descricao: str
    estabelecimento_cnpj: str
    estabelecimento_nome: str
    portador_nome: str


class ContratoArmazenado(_Registro):
    unidade_gestora_codigo: str
    numero: str
    objeto: str
    situacao: str
    modalidade: str
    fornecedor_cnpj: str
    fornecedor_nome: str
    data_assinatura: dt.date | None
    data_inicio_vigencia: dt.date | None
    data_fim_vigencia: dt.date | None
    valor_inicial: float
    valor_final: float


class LicitacaoArmazenada(_Registro):
    unidade_gestora_codigo: str
    situacao: str | None
    modalidade: str | None
    instrumento_legal: str | None
    valor: float | None
    data_abertura: dt.date | None
    data_publicacao: dt.date | None


class ViagemArmazenada(_Registro):
    pcdp: str
    situacao: str
    tipo_viagem: str
    beneficiario_nome: str
    data_inicio_afastamento: dt.date | None
    data_fim_afastamento: dt.date | None
    valor_total_diarias: float
    valor_total_passagem: float
    valor_total_viagem: float
