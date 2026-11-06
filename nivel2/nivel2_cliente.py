import Pyro4


# Configuración del Name Server
IP_SERVIDOR = "172.17.44.86 "
PUERTO_NAMESERVER = 9090

NOMBRE_SERVICIO = "practica.mensajeria"


def mostrar_menu():

    print("\n======================================")
    print("        SISTEMA DE MENSAJERÍA")
    print("======================================")
    print("1. Enviar mensaje")
    print("2. Ver mensajes recibidos")
    print("3. Ver cantidad de mensajes")
    print("4. Salir")
    print("======================================")


def main():

    print("=" * 50)
    print("             CLIENTE PYRO4")
    print("          SISTEMA DE MENSAJERÍA")
    print("=" * 50)

    usuario = input("\nIngrese su nombre: ").strip()

    if not usuario:
        print("Debe ingresar un nombre.")
        return

    try:

        print("\nBuscando el Name Server...")

        ns = Pyro4.locateNS(
            host=IP_SERVIDOR,
            port=PUERTO_NAMESERVER
        )

        print("Name Server encontrado correctamente.")

        print("\nBuscando servicio de mensajería...")

        uri = ns.lookup(NOMBRE_SERVICIO)

        print("Servicio localizado correctamente.")
        print(f"URI del servicio: {uri}")

        with Pyro4.Proxy(uri) as servidor:

            servidor._pyroBind()

            print("\nConectado al servidor de mensajería.")

            while True:

                mostrar_menu()

                opcion = input(
                    "\nSeleccione una opción: "
                )

                try:

                    if opcion == "1":

                        mensaje = input(
                            "\nEscriba su mensaje: "
                        )

                        respuesta = servidor.enviar_mensaje(
                            usuario,
                            mensaje
                        )

                        print(f"\n{respuesta}")

                    elif opcion == "2":

                        mensajes = servidor.recibir_mensajes()

                        print("\n========== MENSAJES ==========")

                        if not mensajes:
                            print("No existen mensajes.")

                        else:
                            for mensaje in mensajes:

                                print(
                                    f"\n[{mensaje['hora']}] "
                                    f"{mensaje['usuario']}: "
                                    f"{mensaje['mensaje']}"
                                )

                        print("==============================")

                    elif opcion == "3":

                        cantidad = servidor.cantidad_mensajes()

                        print(
                            f"\nTotal de mensajes: {cantidad}"
                        )

                    elif opcion == "4":

                        print("\nCerrando cliente...")
                        break

                    else:

                        print("\nOpción incorrecta.")

                except Pyro4.errors.PyroError as error:
                    print(f"\nError remoto: {error}")

                except ValueError as error:
                    print(f"\nError: {error}")

    except Pyro4.errors.PyroError as error:

        print("\nERROR DE CONEXIÓN")
        print(f"Detalle: {error}")

        print("\nCompruebe:")
        print("1. Que el Name Server esté encendido.")
        print("2. Que el servidor esté ejecutándose.")
        print("3. Que la IP y los puertos sean correctos.")


if __name__ == "__main__":
    main()