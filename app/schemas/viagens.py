from pydantic import BaseModel


class InfoViagem(BaseModel):
    motivo: str
    pcdp: str
    ano: int
    numPcdp: str
    justificativaUrgente: str | None = None
    urgenciaViagem: str | None = None


class Beneficiario(BaseModel):
    cpfFormatado: str
    nis: str
    nome: str


class Cargo(BaseModel):
    codigoSIAPE: str
    descricao: str


class OrgaoViagem(BaseModel):
    nome: str
    codigoSIAFI: str
    cnpj: str
    sigla: str
    descricaoPoder: str


class UnidadeGestoraViagem(BaseModel):
    codigo: str
    nome: str
    descricaoPoder: str


class Viagem(BaseModel):
    id: int
    viagem: InfoViagem
    situacao: str
    beneficiario: Beneficiario
    cargo: Cargo
    funcao: Cargo
    tipoViagem: str
    orgao: OrgaoViagem
    dataInicioAfastamento: str
    dataFimAfastamento: str
    valorTotalDiarias: float
    valorTotalPassagem: float
    valorTotalViagem: float
    valorTotalDevolucao: float
    valorTotalRestituicao: float
    valorMulta: float
    valorTotalTaxaAgenciamento: float
