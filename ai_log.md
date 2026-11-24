# Bitácora de IA · Actividad 3

**24 de noviembre de 2026 · ChatGPT.** Diseño, análisis y pruebas de una API autenticada para `v2-revisor`.

## Solicitud de diseño y borrador evaluado

> Diseña el servicio de la Actividad 3 aprovechando `api/auth.py` del Laboratorio 3. Propón rutas, modelo de entrada, estados HTTP, control de sesión y límites para conectar `v2-revisor` al motor original. Analiza el `login()` de la consigna. Plantea tres mejoras verificables con énfasis en seguridad, eficiencia y mantenibilidad, y pruebas con casos positivos y negativos.

**Respuesta de diseño evaluada.** Reusar registro y token, conservar la ruta genérica del kit como salida inicial, aceptar JSON de código y comprobar el token y su vigencia. Para el `login()` se propuso concentrar los controles en la versión segura, precargar un diccionario de hashes para la eficiente e inyectar dependencias para la mantenible. El esquema inicial de pruebas cubría éxito, contraseña incorrecta, usuario inexistente y un token inválido.

| Decisión | Hallazgo y criterio | Verificación |
|---|---|---|
| Aceptado | Reutilizar PBKDF2 con sal y `compare_digest`. **SEC-06** orienta la revisión criptográfica. | Pruebas de persistencia, login y firma. |
| Modificado | La ruta genérica dejaba ambiguo qué motor se ejecutaba y el modelo JSON carecía de límites. **SEC-04** orienta la validación de entrada. | Ruta fija `v2-revisor`, cuerpo estricto y dos casos con el motor del equipo. |
| Modificado | La propuesta inicial enumeraba estados HTTP y dejaba pendiente el formato de error. **ing-07** especifica `problem+json`. | Las pruebas comprueban contenido, estado y `trace_id`, además del resultado. |
| Modificado | Al documentar la autenticación era necesario limitar el contenido del registro de intentos. **ing-02** guía el manejo de secretos y **SEC-03** los registros. | La prueba inspecciona las columnas de la bitácora. El secreto de firma se configura en el entorno. |
| Rechazado | Usar una ruta con respuestas de demostración como evidencia de integración. | La prueba hace la petición HTTP y observa cuatro llamadas en el motor fijado. Las respuestas del proveedor están simuladas y se declaran como tales. |
| Rechazado | Comprobar el token inválido con una sola prueba genérica. Un error 401 podría ocultar una clase de falla distinta. | Casos separados para ausencia, expiración y alteración de firma, más bloqueo, entrada inválida y cuota. |

La evidencia de eficiencia mide accesos al diccionario con un espía. La comparación conserva el trabajo criptográfico para una cuenta inexistente. Las pruebas automatizadas usan cuentas ficticias y un secreto generado por sesión.
