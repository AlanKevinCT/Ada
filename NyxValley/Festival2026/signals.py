from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Reservacion, Parque


# ─────────────────────────────────────────────────────────────
#  SignalCorreoCliente  (del diagrama — patrón Observer)
#  Observa cambios en Reservacion y notifica al cliente
#  por correo electrónico (RF-11)
# ─────────────────────────────────────────────────────────────

class SignalCorreoCliente:

    @staticmethod
    def notifyReserva(cliente, reservacion):
        """Notifica al cliente cuando su reservación es confirmada."""
        send_mail(
            subject='✨ Reservación confirmada — Festival de las Luciérnagas',
            message=(
                f'Hola {cliente.nombre},\n\n'
                f'Tu reservación ha sido confirmada con los siguientes datos:\n\n'
                f'  Parque:          {reservacion.parque.nombre}\n'
                f'  Fecha de inicio: {reservacion.fecha_inicio}\n'
                f'  Fecha de fin:    {reservacion.fecha_fin}\n'
                f'  Personas:        {reservacion.numero_personas}\n'
                f'  Tipo de visita:  {reservacion.get_tipo_visita_display()}\n\n'
                f'¡Te esperamos en el festival!\n'
                f'— Equipo Luciernaguitas 🌿'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[cliente.correo_electronico],
            fail_silently=True,
        )

    @staticmethod
    def notifyCancelar(cliente, reservacion):
        """Notifica al cliente cuando su reservación es cancelada."""
        send_mail(
            subject='Reservación cancelada — Festival de las Luciérnagas',
            message=(
                f'Hola {cliente.nombre},\n\n'
                f'Tu reservación en {reservacion.parque.nombre} '
                f'del {reservacion.fecha_inicio} al {reservacion.fecha_fin} '
                f'ha sido cancelada.\n\n'
                f'Si fue un error puedes volver a reservar desde tu cuenta.\n'
                f'— Equipo Luciernaguitas 🌿'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[cliente.correo_electronico],
            fail_silently=True,
        )

    @staticmethod
    def notifyModificacion(cliente, reservacion):
        """Notifica al cliente cuando su reservación es modificada."""
        send_mail(
            subject='Reservación modificada — Festival de las Luciérnagas',
            message=(
                f'Hola {cliente.nombre},\n\n'
                f'Tu reservación en {reservacion.parque.nombre} '
                f'ha sido modificada:\n\n'
                f'  Nueva fecha de inicio: {reservacion.fecha_inicio}\n'
                f'  Nueva fecha de fin:    {reservacion.fecha_fin}\n\n'
                f'— Equipo Luciernaguitas 🌿'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[cliente.correo_electronico],
            fail_silently=True,
        )

    @staticmethod
    def notifyActualizacion(cliente, mensaje: str):
        """Notifica al cliente cuando un parque de su reservación es modificado."""
        send_mail(
            subject='Actualización de parque — Festival de las Luciérnagas',
            message=(
                f'Hola {cliente.nombre},\n\n'
                f'{mensaje}\n\n'
                f'— Equipo Luciernaguitas 🌿'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[cliente.correo_electronico],
            fail_silently=True,
        )
    
    @staticmethod
    def notifyRegistro(cliente):
        """Correo de bienvenida al registrarse (además del de reservación)."""
        send_mail(
            subject='¡Bienvenido al Festival Internacional de las Luciérnagas 2026!',
            message=(
                f'Hola {cliente.nombre},\n\n'
                f'Tu cuenta ha sido creada exitosamente con el correo: '
                f'{cliente.correo_electronico}\n\n'
                f'Ya puedes explorar los parques y realizar tu reservación.\n\n'
                f'¡Te esperamos en el festival!\n'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[cliente.correo_electronico],
            fail_silently=True,
        )


# ─────────────────────────────────────────────────────────────
#  SignalModificacion  (del diagrama — patrón Observer)
#  Observa cambios en Parque y notifica a usuarios afectados
# ─────────────────────────────────────────────────────────────

class SignalModificacion:

    @staticmethod
    def borrarParque(parque: Parque):
        """
        Cuando se elimina un parque, notifica a todos los clientes
        con reservaciones activas en ese parque.
        """
        reservaciones = Reservacion.objects.filter(
            parque=parque, estado='activa'
        )
        for reservacion in reservaciones:
            SignalCorreoCliente.notifyActualizacion(
                reservacion.usuario,
                f'El parque {parque.nombre} ha sido eliminado del festival. '
                f'Tu reservación ha sido cancelada automáticamente.'
            )
            reservacion.estado = 'cancelada'
            reservacion.save()

    @staticmethod
    def agregarParque(parque: Parque):
        """Cuando se agrega un parque — por ahora solo registra la acción."""
        pass

    @staticmethod
    def modificarParque(parque: Parque, cambios: str):
        """
        Cuando se modifica un parque, notifica a todos los clientes
        con reservaciones activas en ese parque.
        """
        reservaciones = Reservacion.objects.filter(
            parque=parque, estado='activa'
        )
        for reservacion in reservaciones:
            SignalCorreoCliente.notifyActualizacion(
                reservacion.usuario,
                f'El parque {parque.nombre} ha sido actualizado: {cambios}'
            )


# ─────────────────────────────────────────────────────────────
#  Conexión automática con Django signals (post_save)
#  Esto dispara notifyReserva cada vez que se crea
#  una Reservacion nueva — implementa el «include» de CU-06
# ─────────────────────────────────────────────────────────────

@receiver(post_save, sender=Reservacion)
def al_crear_reservacion(sender, instance, created, **kwargs):
    """Se dispara automáticamente cuando se guarda una Reservacion nueva."""
    if created and instance.estado == 'activa':
        SignalCorreoCliente.notifyReserva(instance.usuario, instance)