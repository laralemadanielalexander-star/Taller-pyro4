import Pyro4
import threading
import time

from datetime import datetime


# CONFIGURACIÓN DEL SERVIDOR
IP_SERVIDOR = "172.17.44.86"
PUERTO = 9094


@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class ProcesadorDatos:
    """Servicio remoto para procesamiento de números primos."""

    def __init__(self):
        self.contador = 0
        self.lock = threading.Lock()

    def es_primo(self, numero):
        """Comprueba si un número es primo."""

        if numero < 2:
            return False

        divisor = 2

        while divisor * divisor <= numero:
            if numero % divisor == 0:
                return False

            divisor += 1

        return True

    def procesar_datos(self, limite):
        """Procesa números primos hasta el límite recibido."""

        if not isinstance(limite, int) or isinstance(limite, bool):
            raise ValueError("El límite debe ser un número entero.")

        if limite < 1000 or limite > 200000:
            raise ValueError(
                "El límite debe estar entre 1000 y 200000."
            )

        with self.lock:
            self.contador += 1
            id_tarea = self.contador

        hilo = threading.current_thread().name

        inicio = time.time()

        print("\n===================================")
        print(f"[SERVIDOR] Nueva tarea: {id_tarea}")
        print(f"[SERVIDOR] Hilo: {hilo}")
        print(f"[SERVIDOR] Procesando hasta: {limite}")
        print("===================================")

        cantidad_primos = 0
        ultimo_primo = None

        for numero in range(2, limite + 1):

            if self.es_primo(numero):
                cantidad_primos += 1
                ultimo_primo = numero

        # Simulación de una fase adicional de procesamiento.
        # Permite observar el comportamiento asíncrono.
        time.sleep(5)

        duracion = round(time.time() - inicio, 2)

        resultado = {
            "id_tarea": id_tarea,
            "limite": limite,
            "cantidad_primos": cantidad_primos,
            "ultimo_primo": ultimo_primo,
            "duracion": duracion,
            "hilo": hilo
        }

        hora = datetime.now().strftime("%H:%M:%S")

        print("\n-----------------------------------")
        print(f"[{hora}] Tarea {id_tarea} completada")
        print(f"Números procesados: {limite}")
        print(f"Cantidad de primos: {cantidad_primos}")
        print(f"Tiempo empleado: {duracion} segundos")
        print("-----------------------------------")

        return resultado


def main():

    print("=" * 55)
    print("        SERVIDOR DE PROCESAMIENTO")
    print("             ASÍNCRONO PYRO4")
    print("=" * 55)

    # Crear el servidor
    daemon = Pyro4.Daemon(
        host=IP_SERVIDOR,
        port=PUERTO
    )

    # Registrar la clase remota
    uri = daemon.register(
        ProcesadorDatos,
        objectId="procesador"
    )

    print(f"IP del servidor: {IP_SERVIDOR}")
    print(f"Puerto: {PUERTO}")
    print(f"URI: {uri}")

    print("\nServidor iniciado correctamente.")
    print("Esperando solicitudes de procesamiento...")
    print("=" * 55)

    try:
        daemon.requestLoop()

    except KeyboardInterrupt:
        print("\nServidor detenido.")

    finally:
        daemon.close()


if __name__ == "__main__":
    main()