"""Separa el acceso a cuentas de la política de autenticación."""
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from a3.resultado import ACEPTADO, DENEGADO, ResultadoLogin
from api.auth import verificar_contrasena


class RepositorioCredenciales(Protocol):
    def buscar_hash(self, cuenta: str) -> str | None: ...


@dataclass(frozen=True)
class ServicioLogin:
    repositorio: RepositorioCredenciales
    hash_auxiliar: str
    verificar: Callable[[str, str], bool] = verificar_contrasena

    def autenticar(self, cuenta: str, clave: str) -> ResultadoLogin:
        guardado = self.repositorio.buscar_hash(cuenta.strip().lower())
        coincide = self.verificar(clave, guardado if guardado is not None else self.hash_auxiliar)
        return ACEPTADO if guardado is not None and coincide else DENEGADO


def login(user: str, password: str, servicio: ServicioLogin) -> ResultadoLogin:
    return servicio.autenticar(user, password)
