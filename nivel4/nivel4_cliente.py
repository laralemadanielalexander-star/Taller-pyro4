import Pyro4
import time


# CONFIGURACIÓN
IP_SERVIDOR = "172.17.44.86 "
PUERTO = 9094

URI = f"PYRO:procesador@{IP_SERVIDOR}:{PUERTO}"


def mostrar_menu():
    """Muestra el menú de procesamiento."""

    print("\n========================================")
    print("      CLIENTE DE PROCESAMIENTO")
    print("           ASÍNCRONO PYRO4")
    print("========================================")
    print("1. Procesar 100000 números")
    print("2. Procesar 150000 números")
    print("3. Ingresar cantidad personalizada")
    print("4. Salir")
    print("========================================")


def mostrar_resultado(resultado):
    """Muestra los resultados devueltos por el servidor."""

    print("\n========================================")
    print("       PROCESAMIENTO FINALIZADO")
    print("========================================")

    print(f"Tarea: {resultado['id_tarea']}")
    print(f"Números procesados: {resultado['limite']}")
    print(
        f"Cantidad de números primos: "
        f"{resultado['cantidad_primos']}"
    )
    print(f"Último número primo: {resultado['ultimo_primo']}")
    print(f"Tiempo del servidor: {resultado['duracion']} s")
    print(f"Hilo utilizado: {resultado['hilo']}")

    print("========================================")


def main():

    print("=" * 50)
    print("          CLIENTE ASÍNCRONO")
    print("               PYRO4")
    print("=" * 50)

    print(f"Servidor: {IP_SERVIDOR}")
    print(f"Puerto: {PUERTO}")

    try:

        with Pyro4.Proxy(URI) as servidor:

            servidor._pyroBind()

            print("\nConectado correctamente al servidor.")

            # Habilitar llamadas remotas asíncronas.
            Pyro4.asyncproxy(servidor)

            print("Modo asíncrono activado.")

            while True:

                mostrar_menu()

                opcion = input(
                    "\nSeleccione una opción: "
                )

                if opcion == "1":
                    limite = 100000

                elif opcion == "2":
                    limite = 150000

                elif opcion == "3":

                    try:
                        limite = int(
                            input(
                                "Ingrese un límite "
                                "(1000 - 200000): "
                            )
                        )

                    except ValueError:
                        print("Debe ingresar un número entero.")
                        continue

                elif opcion == "4":
                    print("\nCerrando cliente...")
                    break

                else:
                    print("\nOpción incorrecta.")
                    continue

                try:

                    print("\nEnviando solicitud al servidor...")

                    # LLAMADA ASÍNCRONA
                    futuro = servidor.procesar_datos(limite)

                    print("\nSolicitud enviada.")
                    print("El cliente puede continuar trabajando.")

                    contador = 0

                    # Revisar si el resultado está disponible.
                    while not futuro.ready:

                        contador += 1

                        print(
                            f"[CLIENTE] Realizando otras "
                            f"actividades... {contador}"
                        )

                        # Simula trabajo local del cliente.
                        print(
                            f"[CLIENTE] Cálculo local: "
                            f"{contador} x 10 = {contador * 10}"
                        )

                        time.sleep(1)

                    # Recuperar el resultado remoto.
                    resultado = futuro.value

                    mostrar_resultado(resultado)

                except Exception as error:
                    print(f"\nError en el procesamiento: {error}")

    except Pyro4.errors.CommunicationError as error:

        print("\nERROR DE CONEXIÓN")
        print("No se pudo conectar al servidor.")
        print(f"Detalle: {error}")

    except Pyro4.errors.PyroError as error:

        print(f"\nError de Pyro4: {error}")


if __name__ == "__main__":
    main()