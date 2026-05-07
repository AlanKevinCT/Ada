from abc import ABC, abstractmethod


# ─────────────────────────────────────────────────────────────
#  ServicioParque  (Abstract Class del diagrama)
#  Clase base abstracta del patrón Decorator
# ─────────────────────────────────────────────────────────────
class ServicioParque(ABC):

    @abstractmethod
    def getHorario(self) -> str:
        pass

    @abstractmethod
    def getNombre(self) -> str:
        pass

    @abstractmethod
    def getDireccion(self) -> str:
        pass


# ─────────────────────────────────────────────────────────────
#  ParqueBase  (del diagrama)
#  Implementación concreta base — todo parque tiene camping
# ─────────────────────────────────────────────────────────────
class ParqueBase(ServicioParque):

    def __init__(self, nombre: str, direccion: str, horario: str):
        self._nombre    = nombre
        self._direccion = direccion
        self._horario   = horario

    def getHorario(self) -> str:
        return self._horario

    def getNombre(self) -> str:
        return self._nombre

    def getDireccion(self) -> str:
        return self._direccion

    def __str__(self):
        return f'{self._nombre} — Zona de camping incluida'


# ─────────────────────────────────────────────────────────────
#  ParqueDecorator  (del diagrama)
#  Decorator base — envuelve cualquier ServicioParque
# ─────────────────────────────────────────────────────────────
class ParqueDecorator(ServicioParque):

    def __init__(self, servicio: ServicioParque):
        self._servicio = servicio

    def getHorario(self) -> str:
        return self._servicio.getHorario()

    def getNombre(self) -> str:
        return self._servicio.getNombre()

    def getDireccion(self) -> str:
        return self._servicio.getDireccion()


# ─────────────────────────────────────────────────────────────
#  Cabañas  (del diagrama)
#  Decorator concreto — agrega servicio de cabañas al parque
# ─────────────────────────────────────────────────────────────
class Cabanas(ParqueDecorator):

    def __init__(self, servicio: ServicioParque, tipo: str,
                 capacidad: int):
        super().__init__(servicio)
        self.tipo      = tipo        # ej. "cabaña familiar", "cabaña doble"
        self.capacidad = capacidad

    def getNombre(self) -> str:
        return f'{self._servicio.getNombre()} (+ Cabañas {self.tipo})'

    def __str__(self):
        return (f'{self.getNombre()} — '
                f'Cabañas tipo {self.tipo}, capacidad {self.capacidad}')


# ─────────────────────────────────────────────────────────────
#  servicioParque  (del diagrama)
#  Decorator concreto — agrega servicios extra y capacidad
# ─────────────────────────────────────────────────────────────
class ServicioParqueDecorator(ParqueDecorator):

    def __init__(self, servicio: ServicioParque, servicio_extra: str,
                 horario: str, capacidad: int):
        super().__init__(servicio)
        self.servicio_extra = servicio_extra
        self._horario_extra = horario
        self.capacidad      = capacidad

    def getHorario(self) -> str:
        return self._horario_extra

    def actualizarParque(self, nuevo_servicio: str) -> None:
        """Actualiza el servicio extra del parque."""
        self.servicio_extra = nuevo_servicio

    def __str__(self):
        return (f'{self.getNombre()} — '
                f'Servicio extra: {self.servicio_extra}, '
                f'Capacidad: {self.capacidad}')