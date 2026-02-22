class RoleConfirmationService:
    """
    Servicio para centralizar la validación de roles de usuario.
    """
    @staticmethod
    def is_admin(user):
        """
        Verifica si el usuario tiene el rol de Administrador.
        """
        if not (user and user.is_authenticated):
            return False
        try:
            return user.FK_Role.RoleType == 'Administrador'
        except AttributeError:
            return False

    @staticmethod
    def is_healthcare_professional(user):
        """
        Verifica si el usuario tiene el rol de Profesional de la Salud.
        """
        if not (user and user.is_authenticated):
            return False
        try:
            # Nota: El RoleType exacto se asume como 'Profesional de la Salud'.
            # Se debe ajustar si el nombre en el diccionario es distinto.
            return user.FK_Role.RoleType == 'Profesional de la Salud'
        except AttributeError:
            return False
