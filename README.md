# Actividad 3 · FinNorte v2-revisor

Entrega individual LSCA2318 · Luis Alfonso Juárez Amaro · `Lolmastercraft`.

El servicio REST integra el registro, inicio de sesión y token del laboratorio con el motor del Avance 1. El endpoint autenticado `POST /v1/v2-revisor` recibe `{"codigo": "<texto Python>"}` y llama a `finnorte.variante.sistema` en la revisión `6c1835b1a556240382c3d678ecec6bf0af6f5948` del [repositorio del equipo](https://github.com/alanrivera066/Project_v2_TSTI).

## Ejecución

Con Python 3.10 o posterior y Git, desde la raíz y en un entorno virtual activo:

```text
python -m pip install -r requirements.txt
python -m guia.preparar_motor
python -m pytest tests/test_a3_*.py -v
```

En PowerShell, ejecuta `python -m pytest tests -v` para que pytest descubra los archivos sin depender de la expansión del comodín. El instalador obtiene la revisión fijada en `.motor/`; el código y el corpus del equipo se preparan localmente. Las pruebas de integración usan `fake` con las respuestas de demostración del propio equipo y validan las cuatro etapas del motor.

Para abrir la API, copia `.env.example` a `.env` y coloca un valor generado por `python -c "import secrets; print(secrets.token_hex(32))"` en `TOKEN_SECRET`. En modo interactivo con proveedor real, configura `LLM_PROVIDER=gemini`, `EMB_PROVIDER=gemini` y `GEMINI_API_KEY` en el mismo `.env` local. Inicia el servicio:

```text
python -m uvicorn api.producto:app --env-file .env
```

En [Swagger local](http://127.0.0.1:8000/docs), registra una cuenta, inicia sesión, pega el token en **Authorize** y llama a `/v1/v2-revisor`. `codigo` admite texto Python válido de hasta 30,000 caracteres. El límite predeterminado es de 30 solicitudes autenticadas por cuenta en 60 segundos en cada proceso de servicio. Los errores de API usan `application/problem+json`.

## Evidencias y fuentes

- [Bitácora de IA](ai_log.md) y [análisis de las cuatro versiones](a3/analisis_login.md).
- [GitHub Actions](https://github.com/Lolmastercraft/Actividad-3-TSTDLI/actions) registra pytest y conserva las respuestas de prueba sin secretos.
- [Manual y presentación de la A3](https://github.com/CyberProf-tecmi/lsca2318-lab-a3-a4).
