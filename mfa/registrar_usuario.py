"""Registrar usuarios de laboratorio con contraseñas derivadas por PBKDF2."""
import getpass
import hashlib
import json
import os
import secrets
from pathlib import Path

RUTA = Path(__file__).resolve().parent / "usuarios.json"
ITERACIONES = 300_000


def main():
    usuarios = json.loads(RUTA.read_text(encoding="utf-8")) if RUTA.exists() else {}
    nombre = input("Nuevo nombre de usuario: ").strip().lower()
    if not nombre or len(nombre) > 40 or not nombre.replace("_", "").isalnum():
        print("Usa letras, números o guion bajo (máx. 40 caracteres).")
        return
    if nombre in usuarios:
        print("Ese usuario ya existe.")
        return

    chat_id = input("Chat ID de Telegram (solo números): ").strip()
    if not chat_id.lstrip("-").isdigit():
        print("Chat ID inválido.")
        return

    clave = getpass.getpass("Contraseña para la práctica: ")
    confirmar = getpass.getpass("Repite la contraseña: ")
    if clave != confirmar or len(clave) < 10:
        print("Las contraseñas deben coincidir y tener mínimo 10 caracteres.")
        return

    sal = secrets.token_bytes(16)
    derivada = hashlib.pbkdf2_hmac("sha256", clave.encode(), sal, ITERACIONES)
    usuarios[nombre] = {
        "salt": sal.hex(),
        "hash": derivada.hex(),
        "iteraciones": ITERACIONES,
        "chat_id": chat_id,
    }
    RUTA.write_text(json.dumps(usuarios, indent=2), encoding="utf-8")
    os.chmod(RUTA, 0o600)
    print(f"Usuario '{nombre}' registrado en usuarios.json.")


if __name__ == "__main__":
    main()
