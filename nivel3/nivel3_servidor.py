import Pyro4
import threading

from decimal import Decimal, InvalidOperation
from datetime import datetime


# CONFIGURACIÓN DEL SERVIDOR
IP_SERVIDOR = "172.17.44.86"
PUERTO = 9093


# EXCEPCIÓN PERSONALIZADA
class SaldoInsuficienteError(ValueError):
    """Se produce cuando el saldo no permite realizar un retiro."""
    pass


@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class CuentaBancaria:
    """Cuenta bancaria compartida entre varios clientes."""

    def __init__(self):
        # Saldo inicial: $1000.00
        # Utilizamos centavos para evitar errores con decimales.
        self.saldo_centavos = 100000

        # Protege el saldo cuando varios clientes operan a la vez.
        self.lock = threading.Lock()

        print("[BANCO] Cuenta bancaria inicializada.")
        print("[BANCO] Saldo inicial: $1000.00")

    def convertir_centavos(self, monto):
        """Valida un monto y lo convierte a centavos."""

        try:
            valor = Decimal(str(monto))
        except (InvalidOperation, ValueError, TypeError):
            raise ValueError("Debe ingresar un monto válido.")

        if not valor.is_finite():
            raise ValueError("El monto debe ser finito.")

        if valor <= 0:
            raise ValueError("El monto debe ser mayor que cero.")

        centavos = valor * 100

        if centavos != centavos.to_integral_value():
            raise ValueError(
                "El monto no puede tener más de dos decimales."
            )

        return int(centavos)

    def registrar(self, operacion, monto, saldo):
        """Registra las transacciones en el servidor."""

        hora = datetime.now().strftime("%H:%M:%S")

        print(
            f"[{hora}] {operacion} | "
            f"Monto: ${monto / 100:.2f} | "
            f"Saldo: ${saldo / 100:.2f}",
            flush=True
        )

    def consultar_saldo(self):
        """Consulta el saldo actual de la cuenta."""

        with self.lock:
            saldo = self.saldo_centavos

        print(
            f"[BANCO] Consulta de saldo: ${saldo / 100:.2f}",
            flush=True
        )

        return saldo / 100

    def depositar(self, monto):
        """Agrega dinero a la cuenta."""

        centavos = self.convertir_centavos(monto)

        with self.lock:
            self.saldo_centavos += centavos
            saldo = self.saldo_centavos

            self.registrar(
                "DEPÓSITO",
                centavos,
                saldo
            )

        return saldo / 100

    def retirar(self, monto):
        """Retira dinero si existe saldo suficiente."""

        centavos = self.convertir_centavos(monto)

        with self.lock:

            if centavos > self.saldo_centavos:
                raise SaldoInsuficienteError(
                    "Saldo insuficiente para realizar el retiro."
                )

            self.saldo_centavos -= centavos
            saldo = self.saldo_centavos

            self.registrar(
                "RETIRO",
                centavos,
                saldo
            )

        return saldo / 100


def main():

    print("=" * 55)
    print("           BANCO DISTRIBUIDO")
    print("              PYRO4")
    print("=" * 55)

    # Crear demonio Pyro4
    daemon = Pyro4.Daemon(
        host=IP_SERVIDOR,
        port=PUERTO
    )

    # Registrar la CLASE para utilizar instance_mode="single"
    uri = daemon.register(
        CuentaBancaria,
        objectId="banco"
    )

    print(f"IP del servidor: {IP_SERVIDOR}")
    print(f"Puerto: {PUERTO}")
    print(f"URI: {uri}")

    print("\nServidor bancario iniciado correctamente.")
    print("Esperando conexiones de clientes...")
    print("Presiona Ctrl + C para detener el servidor.")
    print("=" * 55)

    try:
        daemon.requestLoop()

    except KeyboardInterrupt:
        print("\n[BANCO] Servidor detenido.")

    finally:
        daemon.close()


if __name__ == "__main__":
    main()