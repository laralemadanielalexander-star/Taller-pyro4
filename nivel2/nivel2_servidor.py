import Pyro4
import threading
from datetime import datetime


# Configuración del servidor
IP_SERVIDOR = "172.17.44.86 "
PUERTO_SERVICIO = 9092
PUERTO_NAMESERVER = 9090

NOMBRE_SERVICIO = "practica.mensajeria"


@Pyro4.expose
class ServicioMensajes:
    """Servicio distribuido de mensajería con Pyro4."""

    def __init__(self):
        self.mensajes = []
        self.lock = threading.Lock()

    def enviar_mensaje(self, usuario, mensaje):
        """Recibe y almacena un mensaje."""

        usuario = usuario.strip()
        mensaje = mensaje.strip()

        if not usuario or not mensaje:
            raise ValueError(
                "El usuario y el mensaje no pueden estar vacíos."
            )

        fecha = datetime.now().strftime("%H:%M:%S")

        nuevo_mensaje = {
            "usuario": usuario,
            "mensaje": mensaje,
            "hora": fecha
        }

        with self.lock:
            self.mensajes.append(nuevo_mensaje)

        print(
            f"[{fecha}] Mensaje de {usuario}: {mensaje}",
            flush=True
        )

        return "Mensaje enviado correctamente."

    def recibir_mensajes(self):
        """Devuelve los mensajes almacenados."""

        with self.lock:
            return list(self.mensajes)

    def cantidad_mensajes(self):
        """Devuelve la cantidad de mensajes recibidos."""

        with self.lock:
            return len(self.mensajes)


def main():

    print("=" * 55)
    print("          SERVIDOR DE MENSAJERÍA")
    print("                 PYRO4")
    print("=" * 55)

    daemon = Pyro4.Daemon(
        host=IP_SERVIDOR,
        port=PUERTO_SERVICIO
    )

    servicio = ServicioMensajes()

    uri = daemon.register(
        servicio,
        objectId="ServicioMensajes"
    )

    print("\nConectando con el Name Server...")

    ns = Pyro4.locateNS(
        host=IP_SERVIDOR,
        port=PUERTO_NAMESERVER
    )

    ns.register(
        NOMBRE_SERVICIO,
        uri,
        safe=False
    )

    print("\nServidor registrado correctamente.")
    print(f"Nombre: {NOMBRE_SERVICIO}")
    print(f"URI: {uri}")
    print(f"IP: {IP_SERVIDOR}")
    print(f"Puerto: {PUERTO_SERVICIO}")

    print("\nEsperando mensajes de los clientes...")
    print("=" * 55)

    try:
        daemon.requestLoop()

    except KeyboardInterrupt:
        print("\nDeteniendo servidor...")

    finally:
        try:
            ns.remove(NOMBRE_SERVICIO)
        except Pyro4.errors.PyroError:
            pass

        daemon.close()


if __name__ == "__main__":
    main()