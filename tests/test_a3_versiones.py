from a3 import login_eficiencia, login_mantenible, login_original, login_seguridad
from api.auth import Autenticador, hash_contrasena, validar_token


def test_original_distingue_usuario_inexistente_y_clave():
    assert login_original.login("admin", "clave-ficticia") != login_original.login("otro", "clave-ficticia")


def test_version_seguridad_emite_token_y_deniega(monkeypatch):
    import secrets
    monkeypatch.setenv("TOKEN_SECRET", secrets.token_hex(32))
    auth = Autenticador()
    try:
        auth.registrar("demo@example.com", "ejemplo-de-prueba")
        salida = login_seguridad.login("demo@example.com", "ejemplo-de-prueba", auth)
        assert salida.aprobado and validar_token(salida.token) == "demo@example.com"
        assert not login_seguridad.login("demo@example.com", "incorrecta", auth).aprobado
    finally:
        auth.db.close()


def test_eficiencia_hace_una_consulta_para_cada_cuenta():
    class Medicion(dict):
        accesos = 0

        def get(self, clave):
            self.accesos += 1
            return super().get(clave)

    cuentas = Medicion({"demo@example.com": hash_contrasena("ejemplo-de-prueba")})
    auxiliar = hash_contrasena("frase-auxiliar-de-prueba")
    assert login_eficiencia.login(" Demo@example.com ", "ejemplo-de-prueba", cuentas, auxiliar).aprobado
    assert cuentas.accesos == 1
    assert not login_eficiencia.login("otro@example.com", "frase-auxiliar-de-prueba", cuentas, auxiliar).aprobado
    assert cuentas.accesos == 2


def test_mantenible_admite_repositorio_y_verificador_inyectados():
    class Repositorio:
        def buscar_hash(self, clave):
            return "hash-de-prueba" if clave == "demo@example.com" else None

    recibidos = []

    def verificar(_clave, huella):
        recibidos.append(huella)
        return True

    servicio = login_mantenible.ServicioLogin(Repositorio(), "hash-auxiliar", verificar)
    assert login_mantenible.login("demo@example.com", "ficticia", servicio).aprobado
    assert not login_mantenible.login("otro@example.com", "ficticia", servicio).aprobado
    assert recibidos == ["hash-de-prueba", "hash-auxiliar"]
