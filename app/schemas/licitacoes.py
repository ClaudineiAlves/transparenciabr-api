from pydantic import BaseModel


class CompraLicitacao(BaseModel):
    numero: str
    objeto: str
    numeroProcesso: str
    contatoResponsavel: str


class UF(BaseModel):
    sigla: str
    nome: str


class Municipio(BaseModel):
    codigoIBGE: str | None = None
    nomeIBGE: str | None = None
    pais: str | None = None
    uf: UF | None = None


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


class Licitacao(BaseModel):
    id: int
    licitacao: CompraLicitacao | None = None
    dataResultadoCompra: str | None = None
    dataAbertura: str | None = None
    dataReferencia: str | None = None
    dataPublicacao: str | None = None
    situacaoCompra: str | None = None
    modalidadeLicitacao: str | None = None
    instrumentoLegal: str | None = None
    valor: float | None = None
    municipio: Municipio | None = None
    unidadeGestora: UnidadeGestora
