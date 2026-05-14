from pydantic import BaseModel


class TipoCartao(BaseModel):
    id: int
    codigo: str
    descricao: str


class Estabelecimento(BaseModel):
    id: int
    cnpjFormatado: str
    cpfFormatado: str
    nome: str
    razaoSocialReceita: str
    nomeFantasiaReceita: str
    tipo: str


class OrgaoVinculado(BaseModel):
    codigoSIAFI: str
    cnpj: str
    sigla: str
    nome: str


class OrgaoMaximo(BaseModel):
    codigo: str
    sigla: str
    nome: str


class UnidadeGestora(BaseModel):
    codigo: str
    nome: str
    descricaoPoder: str
    orgaoVinculado: OrgaoVinculado
    orgaoMaximo: OrgaoMaximo


class Portador(BaseModel):
    cpfFormatado: str
    nis: str
    nome: str


class GastoCartao(BaseModel):
    id: int
    mesExtrato: str
    dataTransacao: str
    valorTransacao: str
    tipoCartao: TipoCartao
    estabelecimento: Estabelecimento
    unidadeGestora: UnidadeGestora
    portador: Portador
