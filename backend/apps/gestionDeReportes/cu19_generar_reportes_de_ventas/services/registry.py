class ReportRegistry:
    """
    Registro central de reportes estáticos y dinámicos del sistema.
    Usa el patrón Registry para facilitar la extensibilidad por código.
    """
    _estaticos = {}
    _dinamicos = {}

    @classmethod
    def register_estatico(cls, nombre, descripcion=""):
        """
        Decorador para registrar una función de reporte estático.
        """
        def decorator(func):
            cls._estaticos[nombre] = {
                "func": func,
                "descripcion": descripcion
            }
            return func
        return decorator

    @classmethod
    def register_dinamico(cls, modelo, label=""):
        """
        Decorador para registrar una clase constructora (Builder) para reporte dinámico.
        """
        def decorator(builder_class):
            cls._dinamicos[modelo] = {
                "class": builder_class,
                "label": label
            }
            return builder_class
        return decorator

    @classmethod
    def get_estatico(cls, nombre):
        if nombre not in cls._estaticos:
            raise ValueError(f"Reporte estático no soportado o no registrado: {nombre}")
        return cls._estaticos[nombre]["func"]

    @classmethod
    def get_dinamico_builder(cls, modelo):
        if modelo not in cls._dinamicos:
            raise ValueError(f"Modelo dinámico no soportado o no registrado: {modelo}")
        return cls._dinamicos[modelo]["class"]

    @classmethod
    def get_opciones_disponibles(cls):
        """
        Retorna los reportes disponibles para mostrar en el frontend.
        """
        return {
            "estaticos": [{"id": k, "nombre": v["descripcion"]} for k, v in cls._estaticos.items()],
            "dinamicos": [{"id": k, "nombre": v["label"]} for k, v in cls._dinamicos.items()]
        }
