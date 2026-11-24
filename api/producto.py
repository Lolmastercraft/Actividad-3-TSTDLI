"""Servicio REST de la Actividad 3 para FinNorte."""
from __future__ import annotations

import ast
import os
import time
from collections import deque
from contextlib import asynccontextmanager
from http import HTTPStatus
from pathlib import Path
from threading import Lock
from typing import Annotated
from uuid import uuid4

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, StringConstraints, field_validator
from starlette.exceptions import HTTPException

from api import auth, motor


class ErrorServicio(Exception):
    def __init__(self, status: int, detalle: str):
        super().__init__(detalle)
        self.status = status


class LimiteSolicitudes:
    def __init__(self, maximo: int):
        self.maximo = maximo
        self.ventanas: dict[str, deque[float]] = {}
        self.candado = Lock()
        self.proxima_limpieza = 0.0

    def contar(self, usuario: str) -> None:
        ahora = time.monotonic()
        with self.candado:
            if ahora >= self.proxima_limpieza:
                self.ventanas = {u: v for u, v in self.ventanas.items() if v[-1] > ahora - 60}
                self.proxima_limpieza = ahora + 60
            ventana = self.ventanas.setdefault(usuario, deque())
            while ventana and ventana[0] <= ahora - 60:
                ventana.popleft()
            if len(ventana) >= self.maximo:
                raise ErrorServicio(429, "Límite de solicitudes por minuto alcanzado.")
            ventana.append(ahora)


class Credenciales(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: Annotated[str, StringConstraints(strict=True, min_length=3, max_length=254)]
    contrasena: Annotated[str, StringConstraints(strict=True, min_length=1, max_length=256)]


class EntradaRevisor(BaseModel):
    model_config = ConfigDict(extra="forbid")
    codigo: Annotated[str, StringConstraints(strict=True, min_length=1, max_length=30_000)]

    @field_validator("codigo")
    @classmethod
    def validar_python(cls, valor: str) -> str:
        if not valor.strip():
            raise ValueError("El código está vacío.")
        try:
            ast.parse(valor)
        except (SyntaxError, ValueError, RecursionError) as exc:
            raise ValueError("El código debe ser Python sintácticamente válido.") from exc
        return valor


def problema(status: int, detalle: str, headers: dict | None = None) -> JSONResponse:
    encabezados = dict(headers or {})
    if status == 401:
        encabezados.setdefault("WWW-Authenticate", "Bearer")
    return JSONResponse(status_code=status, media_type="application/problem+json", headers=encabezados, content={
        "type": "about:blank",
        "title": HTTPStatus(status).phrase,
        "status": status,
        "detail": detalle,
        "trace_id": uuid4().hex,
    })


bearer = HTTPBearer(auto_error=False)


def usuario_actual(request: Request, cred: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]) -> str:
    if cred is None:
        raise ErrorServicio(401, "Se requiere un token Bearer.")
    usuario = auth.validar_token(cred.credentials)
    request.app.state.limite.contar(usuario)
    return usuario


def crear_app(ruta_db: str | None = None, maximo: int | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(servicio: FastAPI):
        ruta = ruta_db or os.getenv("AUTH_DB", str(motor.RAIZ / "bitacora" / "usuarios.db"))
        if ruta != ":memory:":
            Path(ruta).parent.mkdir(parents=True, exist_ok=True)
        servicio.state.auth = auth.Autenticador(ruta)
        servicio.state.limite = LimiteSolicitudes(max(1, maximo if maximo is not None else int(os.getenv("API_LIMITE", "30"))))
        try:
            yield
        finally:
            servicio.state.auth.db.close()

    servicio = FastAPI(title="FinNorte · Actividad 3", lifespan=lifespan)

    @servicio.exception_handler(auth.ErrorAuth)
    @servicio.exception_handler(ErrorServicio)
    async def manejar_error(_request: Request, error: auth.ErrorAuth | ErrorServicio):
        return problema(error.status, str(error))

    @servicio.exception_handler(RequestValidationError)
    async def manejar_validacion(_request: Request, _error: RequestValidationError):
        return problema(422, "La entrada no cumple el formato requerido. Consulta /docs.")

    @servicio.exception_handler(HTTPException)
    async def manejar_http(_request: Request, error: HTTPException):
        return problema(error.status_code, HTTPStatus(error.status_code).phrase, error.headers)

    @servicio.exception_handler(Exception)
    async def manejar_inesperado(_request: Request, _error: Exception):
        return problema(500, "El servicio no pudo procesar la solicitud.")

    @servicio.get("/salud")
    def salud():
        return {"estado": "ok", "variante": "v2-revisor"}

    @servicio.post("/auth/registro", status_code=201)
    def registro(datos: Credenciales, request: Request):
        request.app.state.auth.registrar(datos.email, datos.contrasena)
        return {"mensaje": "Registro exitoso"}

    @servicio.post("/auth/login")
    def login(datos: Credenciales, request: Request):
        token = request.app.state.auth.login(datos.email, datos.contrasena)
        return {"token": token, "tipo": "Bearer", "expira_en_s": auth.VIGENCIA_S}

    @servicio.post("/v1/v2-revisor")
    def ejecutar_revisor(entrada: EntradaRevisor, _usuario: Annotated[str, Depends(usuario_actual)]):
        try:
            return motor.revisar(entrada.codigo)
        except motor.MotorNoDisponible as exc:
            raise ErrorServicio(503, "El motor de revisión no está disponible.") from exc

    return servicio


app = crear_app()
