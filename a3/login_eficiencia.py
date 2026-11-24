"""Consulta una vista precargada de hashes con un solo acceso por intento."""
from collections.abc import Mapping

from a3.resultado import ACEPTADO, DENEGADO, ResultadoLogin
from api.auth import verificar_contrasena


def login(user: str, password: str, usuarios: Mapping[str, str], hash_auxiliar: str) -> ResultadoLogin:
    """Las llaves de usuarios están normalizadas. El hash auxiliar se genera al iniciar."""
    guardado = usuarios.get(user.strip().lower())
    coincide = verificar_contrasena(password, guardado if guardado is not None else hash_auxiliar)
    return ACEPTADO if guardado is not None and coincide else DENEGADO
