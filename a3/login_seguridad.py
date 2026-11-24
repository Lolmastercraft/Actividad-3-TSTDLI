"""Prioriza los controles de autenticación del servicio."""
from a3.resultado import ACEPTADO, DENEGADO, ResultadoLogin
from api.auth import Autenticador, ErrorAuth


def login(user: str, password: str, autenticador: Autenticador) -> ResultadoLogin:
    try:
        token = autenticador.login(user, password)
    except ErrorAuth as error:
        if error.status == 401:
            return DENEGADO
        if error.status == 429:
            return ResultadoLogin(False, str(error))
        raise
    return ResultadoLogin(True, ACEPTADO.mensaje, token)
