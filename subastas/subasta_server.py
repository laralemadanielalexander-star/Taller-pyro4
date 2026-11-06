import Pyro4
import threading
import time
import uuid

from decimal import Decimal, InvalidOperation


IP_SERVIDOR = "172.17.44.86 "
PUERTO_SERVIDOR = 9095
PUERTO_NAMESERVER = 9090

NOMBRE_SERVICIO = "subastas.central"


@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class SistemaSubastas:
    """Servicio central de subastas distribuidas."""

    def __init__(self):
        self.producto = "Laptop"
        self.precio_actual = 10000  # Centavos
        self.duracion = 600  # 10 minutos

        self.inicio = None
        self.ganador = None
        self.ofertas = []
        self.clientes = {}

        self.lock = threading.Lock()

        print("[SERVIDOR] Sistema de subastas preparado.")

    def convertir_monto(self, monto):
        """Convierte dólares a centavos y valida el monto."""

        try:
            valor = Decimal(str(monto))
        except (InvalidOperation, ValueError, TypeError):
            raise ValueError("El monto ingresado no es válido.")

        if not valor.is_finite() or valor <= 0:
            raise ValueError("La oferta debe ser positiva.")

        centavos = valor * 100

        if centavos != centavos.to_integral_value():
            raise ValueError("Utilice máximo dos decimales.")

        return int(centavos)

    def registrar_cliente(self, nombre):
        """Registra un participante en la subasta."""

        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("Debe ingresar un nombre válido.")

        nombre = nombre.strip()

        if len(nombre) > 50:
            raise ValueError("El nombre es demasiado largo.")

        with self.lock:
            if self.inicio is None:
                self.inicio = time.monotonic()
                print("[SERVIDOR] Subasta iniciada.")

            if self.tiempo_restante_interno() <= 0:
                raise ValueError("La subasta ya finalizó.")

            cliente_id = uuid.uuid4().hex

            self.clientes[cliente_id] = nombre

            print(f"[SERVIDOR] Cliente registrado: {nombre}")

            return cliente_id

    def tiempo_restante_interno(self):
        """Calcula el tiempo restante en segundos."""

        if self.inicio is None:
            return self.duracion

        transcurrido = time.monotonic() - self.inicio

        return max(0, self.duracion - transcurrido)

    def consultar_estado(self):
        """Devuelve el estado actual de la subasta."""

        with self.lock:
            restante = self.tiempo_restante_interno()

            return {
                "producto": self.producto,
                "precio": self.precio_actual / 100,
                "ganador": self.ganador,
                "tiempo_restante": int(restante),
                "activa": self.inicio is not None and restante > 0,
                "cantidad_ofertas": len(self.ofertas),
                "cantidad_clientes": len(self.clientes)
            }

    def realizar_oferta(self, cliente_id, monto):
        """Valida y registra una oferta de forma segura."""

        centavos = self.convertir_monto(monto)

        with self.lock:
            if cliente_id not in self.clientes:
                raise ValueError("Cliente no registrado.")

            if self.inicio is None:
                raise ValueError("La subasta no ha comenzado.")

            if self.tiempo_restante_interno() <= 0:
                raise ValueError("La subasta ha finalizado.")

            if centavos <= self.precio_actual:
                raise ValueError(
                    "Oferta rechazada. Debe superar el "
                    f"precio actual de ${self.precio_actual / 100:.2f}"
                )

            nombre = self.clientes[cliente_id]

            self.precio_actual = centavos
            self.ganador = nombre

            self.ofertas.append({
                "cliente": nombre,
                "monto": centavos / 100
            })

            print(
                f"[OFERTA ACEPTADA] {nombre}: "
                f"${centavos / 100:.2f}",
                flush=True
            )

            return {
                "mensaje": "Oferta aceptada correctamente.",
                "precio": centavos / 100,
                "ganador": nombre
            }

    def consultar_historial(self):
        """Devuelve las ofertas aceptadas."""

        with self.lock:
            return [oferta.copy() for oferta in self.ofertas]


def main():
    print("=" * 55)
    print("           SISTEMA DE SUBASTAS")
    print("                PYRO4")
    print("=" * 55)

    daemon = Pyro4.Daemon(
        host=IP_SERVIDOR,
        port=PUERTO_SERVIDOR
    )

    uri = daemon.register(
        SistemaSubastas,
        objectId="subastas"
    )

    print("Conectando con el Name Server...")

    ns = Pyro4.locateNS(
        host=IP_SERVIDOR,
        port=PUERTO_NAMESERVER
    )

    ns.register(NOMBRE_SERVICIO, uri, safe=False)

    print("\nServidor registrado correctamente.")
    print(f"Servicio: {NOMBRE_SERVICIO}")
    print(f"IP: {IP_SERVIDOR}")
    print(f"Puerto: {PUERTO_SERVIDOR}")
    print(f"URI: {uri}")

    print("\nEsperando clientes...")
    print("=" * 55)

    try:
        daemon.requestLoop()

    except KeyboardInterrupt:
        print("\nServidor detenido.")

    finally:
        try:
            ns.remove(NOMBRE_SERVICIO)
        except Pyro4.errors.PyroError:
            pass

        daemon.close()


if __name__ == "__main__":
    main()