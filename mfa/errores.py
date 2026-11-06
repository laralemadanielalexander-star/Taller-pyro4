"""Errores de negocio que se comunican mediante respuestas RPC seguras."""
import Pyro4


class ErrorMFA(Pyro4.errors.SecurityError):
    codigo = "ERROR_MFA"


class CredencialesInvalidas(ErrorMFA):
    codigo = "CREDENCIALES_INVALIDAS"


class CodigoIncorrecto(ErrorMFA):
    codigo = "CODIGO_INCORRECTO"


class CodigoExpirado(ErrorMFA):
    codigo = "CODIGO_EXPIRADO"


class CuentaBloqueada(ErrorMFA):
    codigo = "CUENTA_BLOQUEADA"


class ErrorEnvioTelegram(ErrorMFA):
    codigo = "ERROR_TELEGRAM"


class SesionNoIniciada(ErrorMFA):
    codigo = "SESION_NO_INICIADA"


ERRORES = {cls.codigo: cls for cls in (
    CredencialesInvalidas, CodigoIncorrecto, CodigoExpirado,
    CuentaBloqueada, ErrorEnvioTelegram, SesionNoIniciada
)}
