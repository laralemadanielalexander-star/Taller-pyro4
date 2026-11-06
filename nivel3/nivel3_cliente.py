import Pyro4


# CONFIGURACIÓN DEL SERVIDOR
IP_SERVIDOR = "172.17.44.86"
PUERTO = 9093

URI = f"PYRO:banco@{IP_SERVIDOR}:{PUERTO}"


def mostrar_menu():

    print("\n========================================")
    print("          BANCO DISTRIBUIDO")
    print("========================================")
    print("1. Consultar saldo")
    print("2. Depositar dinero")
    print("3. Retirar dinero")
    print("4. Salir")
    print("========================================")


def main():

    print("=" * 50)
    print("            CLIENTE BANCARIO")
    print("                 PYRO4")
    print("=" * 50)

    nombre = input("Ingrese su nombre: ")

    print(f"\nBienvenido, {nombre}")
    print(f"Servidor bancario: {IP_SERVIDOR}")
    print(f"Puerto: {PUERTO}")

    try:

        with Pyro4.Proxy(URI) as banco:

            # Verificar conexión con el servidor
            banco._pyroBind()

            print("\nConectado correctamente al banco.")

            while True:

                mostrar_menu()

                opcion = input(
                    "\nSeleccione una opción: "
                )

                if opcion == "1":

                    try:
                        saldo = banco.consultar_saldo()

                        print("\n----------------------------")
                        print(f"SALDO ACTUAL: ${saldo:.2f}")
                        print("----------------------------")

                    except Exception as error:
                        print(f"\nError: {error}")

                elif opcion == "2":

                    monto = input(
                        "Ingrese el monto a depositar: $"
                    )

                    try:

                        saldo = banco.depositar(monto)

                        print("\nDEPÓSITO EXITOSO")
                        print(f"Saldo actual: ${saldo:.2f}")

                    except Exception as error:
                        print(f"\nError: {error}")

                elif opcion == "3":

                    monto = input(
                        "Ingrese el monto a retirar: $"
                    )

                    try:

                        saldo = banco.retirar(monto)

                        print("\nRETIRO EXITOSO")
                        print(f"Saldo actual: ${saldo:.2f}")

                    except Exception as error:
                        print(f"\nError: {error}")

                elif opcion == "4":

                    print("\nCerrando sesión bancaria...")
                    break

                else:

                    print("\nOpción incorrecta.")

    except Pyro4.errors.CommunicationError as error:

        print("\nERROR DE CONEXIÓN")
        print("No se pudo conectar con el servidor bancario.")
        print(f"Detalle: {error}")

    except Pyro4.errors.PyroError as error:

        print(f"\nError de Pyro4: {error}")


if __name__ == "__main__":
    main()