"""Servidor de autenticación distribuida con OTP por Telegram (laboratorio)."""
import hashlib
import hmac
import json
import os
from pathlib import Path
import secrets
import threading
import time

import Pyro4
import requests
from errores import (
    ErrorMFA, CredencialesInvalidas, CodigoIncorrecto, CodigoExpirado,
    CuentaBloqueada, ErrorEnvioTelegram, SesionNoIniciada,
)

IP_SERVIDOR = "172.17.44.86"
PUERTO = 9096
RUTA_USUARIOS = Path(__file__).resolve().parent / "usuarios.json"
TTL_OTP = 180  # 3 minutos
MAX_PASSWORD = 5
MAX_OTP = 3
SEGUNDOS_BLOQUEO = 120


@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class ServicioMFA:
    """Una instancia compartida conserva el estado de MFA de los usuarios."""

    def __init__(self):
        self.usuarios = json.loads(RUTA_USUARIOS.read_text(encoding="utf-8"))
        self.intentos_clave = {}
        self.bloqueos = {}
        self.otps = {}
        self.lock = threading.RLock()
        self.token_bot = os.environ["TELEGRAM_BOT_TOKEN"]
        print(f"Usuarios configurados: {len(self.usuarios)}", flush=True)

    def _comprobar_bloqueo(self, usuario):
        ahora = time.monotonic()
        hasta = self.bloqueos.get(usuario, 0)
        if hasta > ahora:
            raise CuentaBloqueada(
                f"Cuenta bloqueada temporalmente. Reintenta en {int(hasta - ahora) + 1} s."
            )
        if hasta:
            self.bloqueos.pop(usuario, None)
            self.intentos_clave.pop(usuario, None)
            self.otps.pop(usuario, None)

    def _bloquear(self, usuario):
        self.bloqueos[usuario] = time.monotonic() + SEGUNDOS_BLOQUEO
        self.intentos_clave.pop(usuario, None)
        self.otps.pop(usuario, None)
        raise CuentaBloqueada("Demasiados intentos. Cuenta bloqueada durante 120 s.")

    def _verificar_password(self, usuario, password):
        registro = self.usuarios.get(usuario)
        if not registro:
            # Respuesta genérica para cuentas no registradas.
            return False
        sal = bytes.fromhex(registro["salt"])
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), sal, int(registro["iteraciones"])
        )
        return hmac.compare_digest(digest, bytes.fromhex(registro["hash"]))

    def _enviar_telegram(self, chat_id, otp):
        url = f"https://api.telegram.org/bot{self.token_bot}/sendMessage"
        try:
            respuesta = requests.post(
                url,
                data={
                    "chat_id": chat_id,
                    "text": f"Código de acceso MFA: {otp}\nCaduca en 3 minutos. No lo compartas.",
                },
                timeout=10,
            )
            respuesta.raise_for_status()
            if not respuesta.json().get("ok"):
                raise ValueError("Telegram no confirmó el envío")
        except (requests.RequestException, ValueError) as exc:
            raise ErrorEnvioTelegram(
                "Telegram no pudo entregar el OTP. Revisa el token, Chat ID e Internet."
            ) from exc

    def _respuesta(self, funcion, *args):
        # Convertimos errores personalizados en códigos transportables usando serpent.
        try:
            return {"ok": True, "mensaje": funcion(*args)}
        except ErrorMFA as exc:
            return {"ok": False, "codigo": exc.codigo, "mensaje": str(exc)}

    def iniciar_sesion(self, usuario, password):
        """Verifica la contraseña y envía un OTP temporal por Telegram."""
        return self._respuesta(self._iniciar_sesion, usuario, password)

    def _iniciar_sesion(self, usuario, password):
        if not isinstance(usuario, str) or not isinstance(password, str):
            raise CredencialesInvalidas("Credenciales inválidas.")
        usuario = usuario.strip().lower()
        with self.lock:
            self._comprobar_bloqueo(usuario)
            if not self._verificar_password(usuario, password):
                self.intentos_clave[usuario] = self.intentos_clave.get(usuario, 0) + 1
                if self.intentos_clave[usuario] >= MAX_PASSWORD:
                    self._bloquear(usuario)
                raise CredencialesInvalidas("Usuario o contraseña incorrectos.")

            self.intentos_clave.pop(usuario, None)
            codigo = f"{secrets.randbelow(1_000_000):06d}"
            # Solo conservar el hash del OTP; no imprimir ni almacenar su valor.
            self._enviar_telegram(self.usuarios[usuario]["chat_id"], codigo)
            self.otps[usuario] = {
                "hash": hashlib.sha256(codigo.encode()).digest(),
                "expira": time.monotonic() + TTL_OTP,
                "intentos": 0,
            }
            print(f"[MFA] OTP enviado a '{usuario}'.", flush=True)
            return "Credenciales correctas. Revisa tu Telegram e ingresa el código de 6 dígitos."

    def verificar_codigo_mfa(self, usuario, codigo):
        """Valida un OTP una sola vez y rechaza códigos expirados."""
        return self._respuesta(self._verificar_codigo, usuario, codigo)

    def _verificar_codigo(self, usuario, codigo):
        if not isinstance(usuario, str) or not isinstance(codigo, str):
            raise CodigoIncorrecto("Formato de código incorrecto.")
        usuario = usuario.strip().lower()
        with self.lock:
            self._comprobar_bloqueo(usuario)
            registro = self.otps.get(usuario)
            if registro is None:
                raise SesionNoIniciada("Primero debes iniciar sesión y solicitar un código.")
            if time.monotonic() >= registro["expira"]:
                del self.otps[usuario]
                raise CodigoExpirado("El código caducó. Inicia sesión otra vez.")

            valido = (len(codigo) == 6 and codigo.isascii() and codigo.isdigit()
                      and hmac.compare_digest(
                          hashlib.sha256(codigo.encode()).digest(), registro["hash"]
                      ))
            if not valido:
                registro["intentos"] += 1
                if registro["intentos"] >= MAX_OTP:
                    self._bloquear(usuario)
                raise CodigoIncorrecto(
                    f"Código incorrecto. Quedan {MAX_OTP - registro['intentos']} intentos."
                )

            del self.otps[usuario]  # De un solo uso.
            print(f"[MFA] Acceso autorizado para '{usuario}'.", flush=True)
            return "AUTENTICACIÓN COMPLETA. Acceso autorizado."


def main():
    if not RUTA_USUARIOS.exists():
        raise SystemExit("Falta usuarios.json. Ejecuta primero registrar_usuario.py")
    if not os.environ.get("TELEGRAM_BOT_TOKEN"):
        raise SystemExit("Falta TELEGRAM_BOT_TOKEN en el entorno del servidor.")

    print("Servidor Pyro4 MFA - Laboratorio")
    with Pyro4.Daemon(host=IP_SERVIDOR, port=PUERTO) as daemon:
        uri = daemon.register(ServicioMFA, objectId="mfa")
        print(f"URI: {uri}")
        print("Esperando clientes (Ctrl+C para salir)...")
        daemon.requestLoop()


if __name__ == "__main__":
    main()
