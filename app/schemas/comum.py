from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Pagina(BaseModel, Generic[T]):
    pagina: int
    itens: list[T]


class ErroDetalhe(BaseModel):
    mensagem: str
