class clientes:
    def __init__(self, cli_id, cli_tipo_documento, cli_nombre, cli_apellido, cli_telefono, cli_direccion, cli_correo):
        self.cli_id = cli_id
        self.cli_tipo_documento = cli_tipo_documento
        self.cli_nombre = cli_nombre
        self.cli_apellido = cli_apellido
        self.cli_telefono = cli_telefono
        self.cli_direccion = cli_direccion
        self.cli_correo = cli_correo

    def todic(self):
        return {
            "cli_id": self.cli_id,
            "cli_tipo_documento": self.cli_tipo_documento,
            "cli_nombre": self.cli_nombre,
            "cli_apellido": self.cli_apellido,
            "cli_telefono": self.cli_telefono,
            "cli_direccion": self.cli_direccion,
            "cli_correo": self.cli_correo
        }