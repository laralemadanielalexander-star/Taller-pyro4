import Pyro4


# Configuración del servidor
IP_SERVIDOR = "172.17.44.86 "
PUERTO = 9091

URI = f"PYRO:calculadora@{IP_SERVIDOR}:{PUERTO}"


def mostrar_menu():
    """Muestra las operaciones disponibles."""

    print("\n======================================")
    print("         CLIENTE 2 - PYRO4")
    print("======================================")
    print("1. Sumar")
    print("2. Restar")
    print("3. Multiplicar")
    print("4. Dividir")
    print("5. Salir")
    print("======================================")


def main():
    print("=" * 50)
    print("             CLIENTE 2")
    print("        CALCULADORA DISTRIBUIDA")
    print("=" * 50)

    print(f"Servidor: {IP_SERVIDOR}")
    print(f"Puerto: {PUERTO}")

    try:
        # Crear proxy para acceder al servidor
        with Pyro4.Proxy(URI) as calculadora:

            # Verificar conexión
            calculadora._pyroBind()

            print("\n¡Conectado correctamente al servidor!")
            print("Cliente 2 listo para realizar operaciones.")

            while True:
                mostrar_menu()

                opcion = input(
                    "\nSeleccione una opción: "
                )

                if opcion == "5":
                    print("\nDesconectando Cliente 2...")
                    break

                if opcion not in ["1", "2", "3", "4"]:
                    print("\nOpción incorrecta.")
                    continue

                try:
                    numero1 = float(
                        input("Ingrese el primer número: ")
                    )

                    numero2 = float(
                        input("Ingrese el segundo número: ")
                    )

                    if opcion == "1":
                        operacion = "SUMA"
                        resultado = calculadora.sumar(
                            numero1, numero2
                        )

                    elif opcion == "2":
                        operacion = "RESTA"
                        resultado = calculadora.restar(
                            numero1, numero2
                        )

                    elif opcion == "3":
                        operacion = "MULTIPLICACION"
                        resultado = calculadora.multiplicar(
                            numero1, numero2
                        )

                    elif opcion == "4":
                        operacion = "DIVISION"
                        resultado = calculadora.dividir(
                            numero1, numero2
                        )

                    print("\n======================================")
                    print(f"OPERACIÓN: {operacion}")
                    print(f"PRIMER NÚMERO: {numero1}")
                    print(f"SEGUNDO NÚMERO: {numero2}")
                    print(f"RESULTADO: {resultado}")
                    print("======================================")

                except ValueError as error:
                    print(f"\nError: {error}")

                except Pyro4.errors.PyroError as error:
                    print(f"\nError remoto: {error}")

    except Pyro4.errors.CommunicationError as error:
        print("\nNo se pudo conectar al servidor.")
        print(f"Detalle: {error}")

        print("\nComprueba:")
        print("1. Que el servidor esté ejecutándose.")
        print("2. Que la IP 172.17.44.91 sea correcta.")
        print("3. Que el puerto 9091 esté disponible.")

    except Pyro4.errors.PyroError as error:
        print(f"\nError de Pyro4: {error}")


if __name__ == "__main__":
    main()