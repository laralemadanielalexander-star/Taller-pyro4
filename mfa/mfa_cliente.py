"""Cliente de MFA mediante Pyro4 para equipos 1, 2 o 3."""
import getpass
import Pyro4
from errores import ERRORES, ErrorMFA

IP_SERVIDOR = "172.17.44.86"
PUERTO = 9096
URI = f"PYRO:mfa@{IP_SERVIDOR}:{PUERTO}"


def interpretar(respuesta):
    if not respuesta["ok"]:
        clase = ERRORES.get(respuesta["codigo"], ErrorMFA)
        raise clase(respuesta["mensaje"])
    return respuesta["mensaje"]


def main():
    print("=== CLIENTE MFA PYRO4 + TELEGRAM ===")
    print(f"Servidor: {IP_SERVIDOR}:{PUERTO}")
    try:
        with Pyro4.Proxy(URI) as servidor:
            servidor._pyroTimeout = 20
            servidor._pyroBind()
            print("Conectado al servidor.")
            while True:
                print("\n1. Iniciar sesión\n2. Salir")
                opcion = input("Opción: ").strip()
                if opcion == "2":
                    break
                if opcion != "1":
                    continue
                usuario = input("Usuario: ").strip().lower()
                password = getpass.getpass("Contraseña: ")
                try:
                    print(interpretar(servidor.iniciar_sesion(usuario, password)))
                    codigo = input("Código de Telegram (6 dígitos): ").strip()
                    print(interpretar(servidor.verificar_codigo_mfa(usuario, codigo)))
                except ErrorMFA as exc:
                    print(f"[ACCESO DENEGADO] {exc.codigo}: {exc}")
                except Pyro4.errors.PyroError as exc:
                    print(f"Error de comunicación Pyro4: {exc}")
    except Pyro4.errors.PyroError as exc:
        print(f"No se pudo conectar con {URI}: {exc}")


if __name__ == "__main__":
    main()
