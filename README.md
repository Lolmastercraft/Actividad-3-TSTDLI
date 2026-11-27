# Actividad 3 · FinNorte v2-revisor

Entrega individual LSCA2318 · `Lolmastercraft`.

Integré el registro, inicio de sesión y token del laboratorio con el motor del Avance 1. El endpoint autenticado `POST /v1/v2-revisor` recibe `{"codigo": "<texto Python>"}` y llama a `finnorte.variante.sistema` en la revisión `6c1835b1a556240382c3d678ecec6bf0af6f5948` del [repositorio del equipo](https://github.com/alanrivera066/Project_v2_TSTI).

## Ejecución

Con Python 3.10 o posterior, desde la raíz y en un entorno virtual activo:

```text
python -m pip install -r requirements.txt
python -m pytest tests -m "not motor_local" -v
```

Las pruebas anteriores verifican la autenticación, las tres versiones y el contrato HTTP sin descargar el repositorio del equipo. Para ejecutar también los casos de integración, abre el ZIP portátil de la entrega, que incluye la revisión fijada en `.motor/`. Con las dependencias ya instaladas, la verificación y la suite con proveedor de prueba se pueden ejecutar sin red:

```text
python -m guia.preparar_motor
python -m pytest tests -v
```

Verifiqué cada archivo portable con el manifiesto SHA-256 de `guia/motor_manifest.json`. Si partes de una copia de GitHub y su origen sigue disponible, puedes preparar el motor con `python -m guia.preparar_motor --descargar`. Esa opción requiere Git y acceso al repositorio del equipo.

## Proveedor y validación

En `.env.example` dejé `LLM_PROVIDER=fake` como valor seguro para pruebas. En una petición manual, `fake` puede responder con HTTP 200, `abstuvo: true`, `artefacto: {}` y el mensaje «REVISIÓN FALLIDA». Ese es el resultado esperado cuando el sustituto no genera el esquema de las etapas. En pytest inyecto las respuestas de prueba del propio equipo, completo el identificador de fuente requerido y compruebo que el motor valida las cuatro etapas y verifica la cita. La integración con esos datos comprueba el servicio.

Para abrir la API, copia `.env.example` a `.env` y coloca un valor generado por `python -c "import secrets; print(secrets.token_hex(32))"` en `TOKEN_SECRET`. En modo interactivo con proveedor real, configura `LLM_PROVIDER=gemini`, `EMB_PROVIDER=gemini` y `GEMINI_API_KEY` en el mismo `.env` local. Inicia el servicio:

```text
python -m uvicorn api.producto:app --env-file .env
```

En [Swagger local](http://127.0.0.1:8000/docs), registra una cuenta, inicia sesión, pega el token en **Authorize** y llama a `/v1/v2-revisor`. `codigo` admite texto Python válido de hasta 30,000 caracteres. El límite predeterminado es de 30 solicitudes autenticadas por cuenta en 60 segundos en cada proceso. Para el 422 devuelvo el campo conocido y la causa, incluida la línea si falla la sintaxis. Los errores usan `application/problem+json`.

Con `GEMINI_API_KEY` configurada en el entorno, `python -m guia.ejecutar_gemini evidencias/gemini.json` revisa `limites.py` y `tokens.py` mediante el endpoint y registra estado, abstención y fuentes. La bitácora de intentos usa el HMAC del correo normalizado, hora y resultado. Una rotación del secreto de firma empieza un nuevo historial de intento por identificador.

## Comparación del login

Conservé `login(user, password)` en los cuatro archivos. En las versiones nuevas cargo la configuración fuera de la llamada. Para repetir la medición de las cuatro versiones y de PBKDF2, ejecuta `python -m guia.medir_login evidencias/tiempos.json`.

## Evidencias y fuentes

- [Bitácora de IA](ai_log.md) y [análisis de las cuatro versiones](a3/analisis_login.md).
- [Corrida con Gemini y artefacto](https://github.com/Lolmastercraft/Actividad-3-TSTDLI/actions/runs/45379207841/job/138393706135).
- [GitHub Actions](https://github.com/Lolmastercraft/Actividad-3-TSTDLI/actions) registra pytest y conserva las respuestas de prueba sin secretos.
- [Manual y presentación de la A3](https://github.com/CyberProf-tecmi/lsca2318-lab-a3-a4).
