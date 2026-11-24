"""Instala el motor del equipo en una copia local, en la revisión de entrega."""
from pathlib import Path
import subprocess

from api.motor import RAIZ, REVISION

REMOTO = "https://github.com/alanrivera066/Project_v2_TSTI.git"
RUTAS = [
    "/src/finnorte/*.py",
    "/prompts/rev_*.md",
    "/prompts/esquemas/rev_*.json",
    "/datos/v2-revisor/codigo/limites.py",
    "/datos/v2-revisor/codigo/tokens.py",
    "/guia/demo_revisor.py",
    *[f"/corpus/v2-revisor/sec-{numero:02d}-*.md" for numero in range(1, 11)],
]


def preparar(destino: Path = RAIZ / ".motor") -> None:
    marcador = destino / "REVISION"
    if marcador.is_file() and marcador.read_text(encoding="ascii").strip() == REVISION:
        return
    destino.mkdir(exist_ok=True)

    def git(*args):
        subprocess.run(["git", "-C", str(destino), *args], check=True)

    if not (destino / ".git").is_dir():
        if any(destino.iterdir()):
            raise RuntimeError(f"La carpeta {destino} ya contiene archivos")
        git("init")
        git("remote", "add", "origin", REMOTO)
    git("config", "remote.origin.promisor", "true")
    git("config", "remote.origin.partialclonefilter", "blob:none")
    git("sparse-checkout", "set", "--no-cone", *RUTAS)
    git("fetch", "--depth=1", "--filter=blob:none", "origin", REVISION)
    git("checkout", "--detach", "FETCH_HEAD")
    marcador.write_text(REVISION + "\n", encoding="ascii")


if __name__ == "__main__":
    preparar()
