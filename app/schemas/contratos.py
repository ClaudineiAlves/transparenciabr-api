from pydantic import BaseModel


class Compra(BaseModel):
    numero: str
    objeto: str
    numeroProcesso: str
    contatoResponsavel: str


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


class Fornecedor(BaseModel):
    id: int
    cpfFormatado: str
    cnpjFormatado: str
    nome: str
    razaoSocialReceita: str
    nomeFantasiaReceita: str
    tipo: str


class Contrato(BaseModel):
    id: int
    numero: str
    objeto: str
    numeroProcesso: str
    fundamentoLegal: str
    compra: Compra | None = None
    situacaoContrato: str
    modalidadeCompra: str
    unidadeGestora: UnidadeGestora
    dataAssinatura: str | None = None
    dataPublicacaoDOU: str | None = None
    dataInicioVigencia: str | None = None
    dataFimVigencia: str | None = None
    fornecedor: Fornecedor
    valorInicialCompra: float
    valorFinalCompra: float
