"""
Validadores reutilizables para campos de formularios.
Centraliza las reglas de longitud máxima por campo.
"""

import re

# ── Detección de emojis ──
# Cubre: emojis Unicode (Emoticons, Symbols, Pictographs, Transport, Flags, etc.)
_EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "\U00002702-\U000027B0"  # dingbats
    "\U000024C2-\U0001F251"  # misc symbols
    "\U0001F900-\U0001F9FF"  # supplemental symbols
    "\U0001FA00-\U0001FA6F"  # chess symbols
    "\U0001FA70-\U0001FAFF"  # symbols extended-A
    "\U00002600-\U000026FF"  # misc symbols
    "\U0000FE00-\U0000FE0F"  # variation selectors
    "\U0000200D"             # zero-width joiner
    "]+",
    re.UNICODE
)


def contiene_emoji(texto):
    """Retorna True si el texto contiene emojis."""
    if texto is None:
        return False
    return bool(_EMOJI_PATTERN.search(str(texto)))


# ── Patrón para nombres y apellidos: solo letras, espacios y tildes ──
_NOMBRE_PATTERN = re.compile(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$')


def validar_nombre_apellido(valor, nombre_campo):
    """
    Valida que un nombre/apellido solo contenga letras, espacios y tildes.
    Retorna None si es válido, o un mensaje de error.
    """
    if not valor or str(valor).strip() == "":
        return None
    if not _NOMBRE_PATTERN.match(str(valor).strip()):
        return f"El campo {nombre_campo} solo puede contener letras y espacios (sin números ni caracteres especiales)"
    return None


# ── Diccionario de límites máximos por campo ──
# Cada entrada: nombre_campo → (max_caracteres, "descripción legible")
LIMITES = {
    # Clientes (BD: cli_nombre varchar(50), cli_correo varchar(100))
    "cli_tipo_documento": (20, "tipo de documento"),
    "cli_nombre": (50, "nombre"),
    "cli_apellido": (50, "apellido"),
    "cli_correo": (100, "correo electrónico"),
    "cli_telefono": (10, "teléfono"),
    "cli_direccion": (200, "dirección"),
    # Productos (BD: pro_nombre varchar(100), pro_descripcion varchar(255))
    "nombre": (100, "nombre del producto"),
    "categoria": (50, "categoría"),
    "descripcion": (255, "descripción"),
    # Proveedores (BD: prov_nombre varchar(100), prov_contacto varchar(20), prov_email varchar(100))
    "nit": (30, "NIT"),
    "prov_nombre": (100, "nombre del proveedor"),
    "contacto": (20, "contacto"),
    "email": (100, "correo electrónico"),
    "direccion": (200, "dirección"),
    "tipo": (30, "tipo"),
    # Usuarios (BD: usu_nombre varchar(100), usu_correo varchar(100))
    "usu_nombre": (100, "nombre de usuario"),
    "usu_correo": (100, "correo electrónico"),
    "usu_contrasena": (255, "contraseña"),
    "usu_rol": (20, "rol"),
    # Pedidos
    "ped_cuenta_bancaria": (50, "cuenta bancaria"),
    "ped_comprobante_tipo": (20, "tipo de comprobante"),
    # Compras
    "com_observacion": (500, "observación"),
    "com_comprobante_tipo": (20, "tipo de comprobante"),
    # Anulaciones
    "anu_motivo": (500, "motivo de anulación"),
    # Inventario / Movimientos
    "inm_motivo": (300, "motivo del movimiento"),
    # Devoluciones
    "motivo": (500, "motivo de devolución"),
    # Facturas
    "forma_pago": (50, "forma de pago"),
    "cuenta_bancaria": (50, "cuenta bancaria"),
    # Lotes
    "lot_numero": (50, "número de lote"),
    # Alertas vencimientos
    "alv_estado": (20, "estado"),
    # Reportes
    "rep_tipo": (50, "tipo de reporte"),
    "rep_parametros": (2000, "parámetros del reporte"),
    "rep_resultado": (5000, "resultado del reporte"),
    # Roles
    "nombre": (50, "nombre"),
    # Sesiones
    "ses_ip": (45, "dirección IP"),
}


def validar_longitud(valor, nombre_campo):
    """
    Valida que un campo string no exceda su límite definido
    y que no contenga emojis.
    Retorna None si es válido, o un mensaje de error si no.
    Ignora campos no definidos en LIMITES.
    """
    if valor is None or nombre_campo not in LIMITES:
        return None

    maximo, legible = LIMITES[nombre_campo]
    texto = str(valor)

    # Rechazar emojis — interfieren con la BD y validaciones
    if contiene_emoji(texto):
        return f"El campo {legible} no puede contener emojis"

    if len(texto) > maximo:
        return f"El campo {legible} no puede tener más de {maximo} caracteres (tiene {len(texto)})"
    return None


def validar_campos_texto(data, *campos):
    """
    Valida múltiples campos de texto de una sola vez.
    Uso: errores = validar_campos_texto(data, "cli_nombre", "cli_correo", ...)
    Retorna lista de mensajes de error (vacía si todo ok).
    """
    errores = []
    for campo in campos:
        if campo in data:
            msg = validar_longitud(data[campo], campo)
            if msg:
                errores.append(msg)
    return errores
