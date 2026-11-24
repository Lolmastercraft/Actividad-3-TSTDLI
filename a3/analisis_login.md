# Análisis comparativo del login oficial

La propuesta de IA fue suficiente para definir responsabilidades iniciales e incompleta para justificar el contrato HTTP, el alcance de la simulación y la medición de eficiencia. La evidencia del estudio se ejecuta con `tests/test_a3_*.py`.

| Problema de la versión original | Impacto | Tipo de mejora | Versión y evidencia |
|---|---|---|---|
| Usuario y contraseña escritos en el código. | Una copia del archivo divulga el acceso de ejemplo. | Manejo de secretos · SEC-01 e ing-02. | Seguridad obtiene la firma del entorno. Las otras versiones reciben hashes desde una dependencia y el servicio de producción persiste PBKDF2 con sal. `test_sqlite_guarda_hash_con_sal_y_bitacora_minima`. |
| Comparación directa de la contraseña. | La comparación directa y los caminos de longitud desigual debilitan el tratamiento de credenciales. | Criptografía · SEC-06. | Las tres verifican un hash; se usa una huella auxiliar cuando falta la cuenta. `test_eficiencia_hace_una_consulta_para_cada_cuenta`. |
| Respuestas distintas para contraseña mala y usuario inexistente. | El texto permite distinguir las causas. | Seguridad y contrato API · ing-07. | Resultado de denegación uniforme y errores con formato estable. `test_oficial_contrasena_incorrecta` y `test_oficial_usuario_inexistente`. |
| Sin sesión, límite ni registro. | Los intentos carecen de una política de contención y trazabilidad. | Seguridad operativa · consigna A3, SEC-03. | Seguridad y servicio real aplican el bloqueo, token de 15 minutos como máximo y registro mínimo. Pruebas de expiración, firma y sexto intento. |
| Mensajes de texto inconsistentes, incluido un espacio final. | Consumidores y pruebas dependen de cadenas concretas. | Mantenibilidad · SEC-10. | Resultado inmutable compartido y repositorio con interfaz verificable. `test_mantenible_admite_repositorio_y_verificador_inyectados`. |

## Cinco criterios comparados

| Criterio | Original | Seguridad | Eficiencia | Mantenible |
|---|---|---|---|---|
| Credenciales | Literales | SQLite con PBKDF2 y sal | Diccionario de hashes precargados | Repositorio de hashes inyectado |
| Resultado inválido | Identifica la causa | Mensaje uniforme y bloqueo temporal | Mensaje uniforme | Mensaje uniforme |
| Sesión y seguimiento | Sin sesión | Token, bloqueo y registro | Resultado local | Resultado local |
| Acceso a datos | Una cuenta fija | Consulta transaccional | Un `get` por intento, medido | Una consulta por interfaz |
| Facilidad de cambio y prueba | Comparaciones y textos acoplados | Controles centralizados en `Autenticador` | Núcleo de función pequeño | Almacenamiento y verificación intercambiables |

Las versiones comparativas enfocadas en eficiencia y mantenibilidad son ejercicios del núcleo de verificación. Para HTTP se emplea la implementación de seguridad de `api/auth.py`.
