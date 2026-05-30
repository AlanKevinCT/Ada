import hashlib
from datetime import date
from .models import Parque, Reservacion


# ─────────────────────────────────────────────────────────────
#  Autenticador  (del diagrama de clases)
#  Maneja el hash SHA-256 de contraseñas (RNF-06)
# ─────────────────────────────────────────────────────────────
class Autenticador:

    @staticmethod
    def contrasenaHash(password: str) -> str:
        """Devuelve el hash SHA-256 de la contraseña."""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def method(tipo: str) -> str:
        """Devuelve el tipo de autenticación usado."""
        return tipo


# ─────────────────────────────────────────────────────────────
#  Disponibilidad  (del diagrama de clases)
#  Valida fechas, horarios y cupo (RF-16, RF-17)
# ─────────────────────────────────────────────────────────────
class Disponibilidad:

    MESES_FESTIVAL = [6, 7, 8]  # junio, julio, agosto

    @staticmethod
    def verificarDisponible(parque: Parque, fecha_inicio: date,
                             fecha_fin: date, tipo_visita: str, cantidad: int) -> bool:
        """Verifica que haya cupo disponible en el parque."""
        reservaciones_activas = Reservacion.objects.filter(
            parque=parque,
            estado='activa',
            tipo_visita=tipo_visita,
            fecha_inicio__lt=fecha_fin,
            fecha_fin__gt=fecha_inicio,
        ).count()
        capacidad_necesaria = reservaciones_activas + cantidad
        print(f"Capacidad del parque {cantidad} capacidad necesaria: {capacidad_necesaria} reservaciones activas: {reservaciones_activas}")
        return capacidad_necesaria <= parque.capacidad

    @staticmethod
    def verificaFechas(fecha_inicio: date, fecha_fin: date) -> bool:
        """
        Valida que las fechas estén dentro del festival
        y que no caigan en martes (RF-16, RF-17).
        """
        hoy = date.today()
        if fecha_inicio < hoy or fecha_fin < hoy:
            return False
        
        if fecha_inicio >= fecha_fin:
            return False

        fecha_actual = fecha_inicio
        while fecha_actual <= fecha_fin:
            # 1 = martes en Python (lunes=0, martes=1...)
            if fecha_actual.weekday() == 1:
                return False
            if fecha_actual.month not in Disponibilidad.MESES_FESTIVAL:
                return False
            from datetime import timedelta
            fecha_actual += timedelta(days=1)

        return True

    @staticmethod
    def verificaHora(hora, parque) -> bool:
        """Verifica que la hora esté dentro del horario del parque."""
        # Se puede extender cuando tengamos horarios por parque
        aceptar = False
        if hora is not None and parque is not None:
            if parque.horario_apertura <= hora <= parque.horario_cierre:
                aceptar = True
        return aceptar


# ─────────────────────────────────────────────────────────────
#  AsistReserva  (del diagrama de clases)
#  Lógica de negocio para reservaciones (RF-04, RF-05)
# ─────────────────────────────────────────────────────────────
class AsistReserva:

    @staticmethod
    def reservar(usuario, parque: Parque, fecha_inicio: date,
                 fecha_fin: date, numero_personas: int,
                 tipo_visita: str) -> Reservacion:
        """Crea una reservación validando fechas y disponibilidad."""

        # usuario_activo = Reservacion.objects.filter(usuario = usuario, parque_nombre = parquenombre)

        if numero_personas <= 0:
            raise ValueError('El número de personas es invalido, introduzca un número positivo.')
        
        if not Disponibilidad.verificaFechas(fecha_inicio, fecha_fin):
            raise ValueError(
                'Las fechas no son válidas: deben estar entre junio y agosto '
                'y no pueden incluir martes.'
            )
        if not Disponibilidad.verificarDisponible(parque, fecha_inicio,
                                                   fecha_fin, tipo_visita, numero_personas):
            raise ValueError('No hay disponibilidad en el parque para esas fechas.')

        reservacion = Reservacion.objects.create(
            usuario=usuario,
            parque=parque,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            numero_personas=numero_personas,
            tipo_visita=tipo_visita,
            estado='activa',
        )
        return reservacion

    @staticmethod
    def cancelarReserva(reservacion: Reservacion) -> bool:
        """Cancela una reservación activa."""
        if reservacion.estado != 'activa':
            return False
        reservacion.estado = 'cancelada'
        reservacion.save()
        return True

    @staticmethod
    def modificarReserva(reservacion: Reservacion, fecha_inicio: date,
                          fecha_fin: date) -> bool:
        if reservacion.estado == 'cancelada':
            return False
        """Modifica las fechas de una reservación activa."""
        if not Disponibilidad.verificaFechas(fecha_inicio, fecha_fin):
            raise ValueError('Las fechas no son válidas.')
        if not Disponibilidad.verificarDisponible(reservacion.parque,
                                                   fecha_inicio, fecha_fin,
                                                   reservacion.tipo_visita, reservacion.numero_personas):
            raise ValueError('No hay disponibilidad para las nuevas fechas.')
        reservacion.fecha_inicio = fecha_inicio
        reservacion.fecha_fin    = fecha_fin
        reservacion.save()
        return True