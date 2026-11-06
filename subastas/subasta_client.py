import Pyro4
import threading
import time


IP_SERVIDOR = "172.17.44.86 "
PUERTO_NAMESERVER = 9090
NOMBRE_SERVICIO = "subastas.central"


def mostrar_estado(estado):
    """Muestra el estado de la subasta."""

    minutos, segundos = divmod(
        estado["tiempo_restante"], 60
    )

    print("\n========================================")
    print("           ESTADO DE SUBASTA")
    print("========================================")
    print(f"Producto: {estado['producto']}")
    print(f"Precio actual: ${estado['precio']:.2f}")
    print(f"Mejor postor: {estado['ganador'] or 'Ninguno'}")
    print(f"Tiempo restante: {minutos:02d}:{segundos:02d}")
    print(f"Ofertas realizadas: {estado['cantidad_ofertas']}")

    if estado["activa"]:
        print("Estado: ACTIVA")
    else:
        print("Estado: FINALIZADA")

    print("========================================")


def mostrar_menu():
    print("\n========== SUBASTAS PYRO4 ==========")
    print("1. Consultar estado de la subasta")
    print("2. Realizar una oferta")
    print("3. Ver historial de ofertas")
    print("4. Salir")
    print("====================================")


def monitorear_subasta(uri, detener):
    """Consulta los cambios de precio cada dos segundos."""

    ultimo_precio = None
    ultima_actividad = None

    try:
        # Cada hilo utiliza su propio proxy Pyro4.
        with Pyro4.Proxy(uri) as servidor:

            while not detener.is_set():
                try:
                    estado = servidor.consultar_estado()

                    precio = estado["precio"]
                    activa = estado["activa"]

                    if ultimo_precio is None:
                        ultimo_precio = precio

                    elif precio != ultimo_precio:
                        print("\n\n*** NUEVA OFERTA ***")
                        print(f"Nuevo precio: ${precio:.2f}")
                        print(
                            "Mejor postor: "
                            f"{estado['ganador']}"
                        )
                        print("********************\n")

                        ultimo_precio = precio

                    if ultima_actividad is True and not activa:
                        print("\n\n*** SUBASTA FINALIZADA ***")
                        print(
                            f"Ganador: "
                            f"{estado['ganador'] or 'Sin ofertas'}"
                        )
                        print(
                            f"Precio final: ${precio:.2f}"
                        )
                        print("**************************\n")

                    ultima_actividad = activa

                except Pyro4.errors.PyroError as error:
                    print(f"\n[MONITOR] Error: {error}")
                    break

                detener.wait(2)

    except Pyro4.errors.PyroError as error:
        print(f"\n[MONITOR] Sin conexión: {error}")


def main():
    print("=" * 50)
    print("             CLIENTE DE SUBASTAS")
    print("                    PYRO4")
    print("=" * 50)

    nombre = input("Ingrese su nombre: ").strip()

    if not nombre:
        print("Debe ingresar un nombre.")
        return

    detener = threading.Event()
    monitor = None

    try:
        print("\nBuscando el Name Server...")

        ns = Pyro4.locateNS(
            host=IP_SERVIDOR,
            port=PUERTO_NAMESERVER
        )

        print("Name Server encontrado.")

        uri = ns.lookup(NOMBRE_SERVICIO)

        print(f"Servicio encontrado: {NOMBRE_SERVICIO}")

        with Pyro4.Proxy(uri) as servidor:

            servidor._pyroBind()

            cliente_id = servidor.registrar_cliente(nombre)

            print(f"\n¡Bienvenido, {nombre}!")
            print("Registro completado correctamente.")

            estado = servidor.consultar_estado()
            mostrar_estado(estado)

            # Hilo de actualizaciones automáticas
            monitor = threading.Thread(
                target=monitorear_subasta,
                args=(uri, detener),
                daemon=True
            )

            monitor.start()

            while True:
                mostrar_menu()

                opcion = input(
                    "\nSeleccione una opción: "
                )

                try:
                    if opcion == "1":

                        estado = servidor.consultar_estado()
                        mostrar_estado(estado)

                    elif opcion == "2":

                        monto = input(
                            "Ingrese su oferta en dólares: $"
                        )

                        resultado = servidor.realizar_oferta(
                            cliente_id,
                            monto
                        )

                        print("\n¡OFERTA ACEPTADA!")
                        print(resultado["mensaje"])
                        print(
                            f"Nuevo precio: "
                            f"${resultado['precio']:.2f}"
                        )

                    elif opcion == "3":

                        historial = servidor.consultar_historial()

                        print("\n====== HISTORIAL DE OFERTAS ======")

                        if not historial:
                            print("Todavía no existen ofertas.")

                        else:
                            for numero, oferta in enumerate(
                                historial, start=1
                            ):
                                print(
                                    f"{numero}. "
                                    f"{oferta['cliente']} - "
                                    f"${oferta['monto']:.2f}"
                                )

                    elif opcion == "4":

                        print("\nCerrando cliente...")
                        break

                    else:

                        print("Opción incorrecta.")

                except ValueError as error:
                    print(f"\nOFERTA RECHAZADA: {error}")

                except Pyro4.errors.PyroError as error:
                    print(f"\nError remoto: {error}")

    except Pyro4.errors.PyroError as error:
        print("\nERROR DE CONEXIÓN")
        print(f"Detalle: {error}")

    finally:
        detener.set()

        if monitor is not None:
            monitor.join(timeout=3)


if __name__ == "__main__":
    main()