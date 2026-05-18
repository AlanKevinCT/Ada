from django.core import mail
from django.test import TestCase
from datetime import date
from ..models import Usuario, Parque, Reservacion
from ..signals import SignalModificacion

class TestSignalsFestival(TestCase):

    def setUp(self):
        """Datos de base para evaluar las notificaciones automáticas."""
        self.usuario = Usuario.objects.create_user(
            correo_electronico='pablo@ciencias.unam.mx',
            nombre='Pablo',
            apellido_paterno='González',
            apellido_materno='Martínez',
            password='password123'
        )
        self.parque = Parque.objects.create(
            nombre='Parque Bicentenario',
            capacidad=50
        )

    # ─────────────────────────────────────────────────────────────
    #  Prueba para SignalCorreoCliente (del diagrama — patrón Observer)
    # ─────────────────────────────────────────────────────────────
    def test_signal_envia_correo_al_crear_reservacion(self):
        """Al crear una reservación activa, se debe disparar automáticamente un correo."""
        # Al inicio, la bandeja de salida simulada está vacía
        self.assertEqual(len(mail.outbox), 0)

        # Disparamos el evento creando la reservación
        Reservacion.objects.create(
            usuario=self.usuario,
            parque=self.parque,
            fecha_inicio=date(2026, 6, 15),
            fecha_fin=date(2026, 6, 18),
            numero_personas=2,
            tipo_visita='camping',
            estado='activa'
        )

        # 1. Validamos que se haya enviado exactamente un correo
        self.assertEqual(len(mail.outbox), 1)
        
        # 2. Validamos los metadatos del correo enviado
        correo = mail.outbox[0]
        self.assertIn('✨ Reservación confirmada — Festival de las Luciérnagas', correo.subject)
        self.assertEqual(correo.to, ['pablo@ciencias.unam.mx'])
        self.assertIn('Parque Bicentenario', correo.body)

    def test_signal_notifica_cancelacion(self):
        """Al cancelar una reservación activa, se debe enviar un correo de cancelación."""
        reserva = Reservacion.objects.create(
            usuario=self.usuario,
            parque=self.parque,
            fecha_inicio=date(2026, 6, 15),
            fecha_fin=date(2026, 6, 18),
            numero_personas=2,
            tipo_visita='camping',
            estado='activa'
        )
        mail.outbox.clear()  # Limpiamos el outbox para evaluar solo la cancelación

        # Simulamos la cancelación de la reservación
        reserva.estado = 'cancelada'
        reserva.save()

        correo = mail.outbox[0]
        
        # Validamos que se envió un correo de cancelación
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Reservación cancelada — Festival de las Luciérnagas', correo.subject)
        self.assertEqual(correo.to, ['pablo@ciencias.unam.mx'])
        self.assertIn('Parque Bicentenario', correo.body)

    def test_signal_notifica_modificacion(self):
        """Al modificar una reservación activa, se debe enviar un correo de actualización."""
        reserva = Reservacion.objects.create(
            usuario=self.usuario,
            parque=self.parque,
            fecha_inicio=date(2026, 6, 15),
            fecha_fin=date(2026, 6, 18),
            numero_personas=2,
            tipo_visita='camping',
            estado='activa'
        )
        mail.outbox.clear()  # Limpiamos el outbox para evaluar solo la modificación

        # Simulamos la modificación de la reservación
        reserva.fecha_inicio = date(2026, 6, 20)
        reserva.fecha_fin = date(2026, 6, 25)
        reserva.save()

        correo = mail.outbox[0]
        
        # Validamos que se envió un correo de actualización
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Reservación modificada — Festival de las Luciérnagas', correo.subject)
        self.assertEqual(correo.to, ['pablo@ciencias.unam.mx'])
        self.assertIn('Parque Bicentenario', correo.body)


    # ─────────────────────────────────────────────────────────────
    #  Pruebas para SignalModificacion (Eventos del Administrador)
    # ─────────────────────────────────────────────────────────────
    def test_signal_borrar_parque_cancela_y_notifica(self):
        """Verifica que al eliminar un parque se cancelen las reservas y se avise por correo."""
        reserva = Reservacion.objects.create(
            usuario=self.usuario, parque=self.parque,
            fecha_inicio=date(2026, 6, 15), fecha_fin=date(2026, 6, 18),
            numero_personas=2, tipo_visita='camping', estado='activa'
        )
        # Limpiamos el outbox (el paso anterior generó el correo de creación)
        mail.outbox.clear()

        # Ejecutamos la lógica de simulación de borrado del parque
        SignalModificacion.borrarParque(self.parque)

        # 1. Comprobamos que el estado de la reserva mutó a 'cancelada'
        reserva.refresh_from_db()
        self.assertEqual(reserva.estado, 'cancelada')

        # 2. Comprobamos que se notificó al usuario sobre la cancelación forzosa
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Actualización de parque — Festival de las Luciérnagas', mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].to, ['pablo@ciencias.unam.mx'])

    def test_signal_modificar_parque_notifica_usuarios(self):
        """Verifica que al alterar los datos de un parque se alerte a los clientes con reservas."""
        Reservacion.objects.create(
            usuario=self.usuario, parque=self.parque,
            fecha_inicio=date(2026, 7, 5), fecha_fin=date(2026, 7, 10),
            numero_personas=2, tipo_visita='camping', estado='activa'
        )
        mail.outbox.clear()

        # Modificamos el parque a través de la señal
        SignalModificacion.modificarParque(self.parque, cambios="Cierre de zona de albercas por mantenimiento.")

        # Validamos que se despachó el aviso por mail
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Actualización de parque — Festival de las Luciérnagas', mail.outbox[0].subject)