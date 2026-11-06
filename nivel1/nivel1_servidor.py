import Pyro4
import threading
from datetime import datetime


@Pyro4.expose
class Calculadora:
    """Servicio de calculadora remota para múltiples clientes."""

    def registrar_operacion(self, operacion, a, b, resultado):
        """Muestra en el servidor las operaciones recibidas."""
        fecha = datetime.now().strftime("%H:%M:%S")
        hilo = threading.current_thread().name

        print(
            f"[{fecha}] [{hilo}] "
            f"{operacion}: {a} y {b} = {resultado}",
            flush=True
        )

    def sumar(self, a, b):
        resultado = a + b
        self.registrar_operacion("SUMA", a, b, resultado)
        return resultado

    def restar(self, a, b):
        resultado = a - b
        self.registrar_operacion("RESTA", a, b, resultado)
        return resultado

    def multiplicar(self, a, b):
        resultado = a * b
        self.registrar_operacion(
            "MULTIPLICACION", a, b, resultado
        )
        return resultado

    def dividir(self, a, b):
        if b == 0:
            print(
                "[SERVIDOR] Error: división entre cero",
                flush=True
            )
            raise ValueError("No se puede dividir entre cero")

        resultado = a / b
        self.registrar_operacion("DIVISION", a, b, resultado)
        return resultado


def main():
    # Configuración del servidor
    ip_servidor = "172.17.44.86 "
    puerto = 9091

    # Crear servidor Pyro4
    daemon = Pyro4.Daemon(
        host=ip_servidor,
        port=puerto
    )

    # Registrar el objeto remoto
    calculadora = Calculadora()

    uri = daemon.register(
        calculadora,
        objectId="calculadora"
    )

    print("=" * 55)
    print("           SERVIDOR PYRO4")
    print("       CALCULADORA DISTRIBUIDA")
    print("=" * 55)

    print(f"IP del servidor: {ip_servidor}")
    print(f"Puerto: {puerto}")
    print(f"URI: {uri}")

    print("\nServidor iniciado correctamente.")
    print("Esperando solicitudes de clientes...")
    print("Presiona Ctrl + C para detenerlo.")

    print("=" * 55)

    try:
        daemon.requestLoop()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        daemon.close()


if __name__ == "__main__":
    main()