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

        self.usuario_extra_1 = Usuario.objects.create_user(
            correo_electronico='Mario@ciencias.unam.mx',
            nombre='Mario',
            apellido_paterno='Pérez',
            apellido_materno='García',
            password='password456'
        )

        self.usuario_extra_2 = Usuario.objects.create_user(
            correo_electronico='Lila@ciencias.unam.mx',
            nombre='Lila',
            apellido_paterno='Naranjo',
            apellido_materno='Morales',
            password='password789'
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
        mail.outbox.clear()  # Limpiamos la bandeja de salida

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

        # Validamos que se envió un correo de cancelación
        self.assertEqual(len(mail.outbox), 1)
        correo = mail.outbox[0]
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
        
        # Validamos que se envió un correo de actualización
        self.assertEqual(len(mail.outbox), 1)
        correo = mail.outbox[0]
        self.assertIn('Reservación modificada — Festival de las Luciérnagas', correo.subject)
        self.assertEqual(correo.to, ['pablo@ciencias.unam.mx'])
        self.assertIn('Parque Bicentenario', correo.body)

    def test_signal_notifica_registro_usuario(self):
        """Envío del correo de bienvenida al registrarse."""
        # Limpiamos la bandeja
        mail.outbox.clear()

        # Creamos un nuevo usuario para disparar la señal de registro
        Usuario.objects.create_user(
            correo_electronico='albert@gmail.com',
            nombre='Alberto',
            apellido_paterno='Pérez',
            apellido_materno='López',
            password='contraseña_segura'
        )

        self.assertEqual(len(mail.outbox), 1)
        correo = mail.outbox[0]
        
        self.assertIn('¡Bienvenido al Festival Internacional de las Luciérnagas 2026!', correo.subject)
        self.assertEqual(correo.to, ['albert@gmail.com'])
        self.assertIn('Hola Alberto', correo.body)
        self.assertIn('Tu cuenta ha sido creada exitosamente con el correo: albert@gmail.com', correo.body)
        self.assertIn('Ya puedes explorar los parques y realizar tu reservación', correo.body)


    # ─────────────────────────────────────────────────────────────
    #  Pruebas para SignalModificacion (Eventos del Administrador)
    # ─────────────────────────────────────────────────────────────
    def test_signal_borrar_parque_cancela_y_notifica(self):
        """Verifica que al eliminar un parque se cancelen en lote las reservas de múltiples usuarios."""
        # 1. Creamos reservaciones activas para los 3 usuarios del festival
        reserva_pablo = Reservacion.objects.create(
            usuario=self.usuario, parque=self.parque,
            fecha_inicio=date(2026, 6, 15), fecha_fin=date(2026, 6, 18),
            numero_personas=2, tipo_visita='camping', estado='activa'
        )
        reserva_Mario = Reservacion.objects.create(
            usuario=self.usuario_extra_1, parque=self.parque,
            fecha_inicio=date(2026, 6, 20), fecha_fin=date(2026, 6, 22),
            numero_personas=1, tipo_visita='cabana', estado='activa'
        )
        reserva_LiLa = Reservacion.objects.create(
            usuario=self.usuario_extra_2, parque=self.parque,
            fecha_inicio=date(2026, 7, 1), fecha_fin=date(2026, 7, 5),
            numero_personas=4, tipo_visita='camping', estado='activa'
        )

        # Limpiamos la bandeja de los 3 correos automáticos generados por la creación
        mail.outbox.clear()

        # 2. Ejecutamos el borrado administrativo del parque
        SignalModificacion.borrarParque(self.parque)

        # 3. Comprobamos la mutación de estado a 'cancelada' para todos
        reserva_pablo.refresh_from_db()
        reserva_Mario.refresh_from_db()
        reserva_LiLa.refresh_from_db()
        self.assertEqual(reserva_pablo.estado, 'cancelada')
        self.assertEqual(reserva_Mario.estado, 'cancelada')
        self.assertEqual(reserva_LiLa.estado, 'cancelada')

        # 4. Validamos el volumen de correos despachados:
        self.assertEqual(len(mail.outbox), 6)

        # 5.  Validamos que los 6 correos tengan asuntos correctos
        asuntos_validos = [
            'Actualización de parque — Festival de las Luciérnagas',
            'Reservación cancelada — Festival de las Luciérnagas'
        ]
        
        for correo in mail.outbox:
            # Cada uno de los 6 correos debe tener uno de los dos asuntos oficiales
            self.assertIn(correo.subject, asuntos_validos)

        # 7. Mapeamos los destinatarios para asegurar que nadie se quedó sin notificación
        destinatarios = [correo.to[0] for correo in mail.outbox]
        self.assertTrue(destinatarios.count('pablo@ciencias.unam.mx'), 2)
        self.assertTrue(destinatarios.count('Lila@ciencias.unam.mx'), 2)
        self.assertTrue(destinatarios.count('Mario@ciencias.unam.mx'), 2)

    def test_signal_modificar_parque_notifica_usuarios(self):
        """Verifica que al alterar los datos de un parque se alerte en lote a todos los clientes vinculados."""
        # Creamos las reservaciones para la audiencia afectada
        Reservacion.objects.create(
            usuario=self.usuario, parque=self.parque,
            fecha_inicio=date(2026, 7, 5), fecha_fin=date(2026, 7, 10),
            numero_personas=2, tipo_visita='camping', estado='activa'
        )
        Reservacion.objects.create(
            usuario=self.usuario_extra_1, parque=self.parque,
            fecha_inicio=date(2026, 7, 12), fecha_fin=date(2026, 7, 15),
            numero_personas=3, tipo_visita='cabana', estado='activa'
        )
        mail.outbox.clear()

        # Modificamos los parámetros del parque
        SignalModificacion.modificarParque(self.parque, cambios="Cierre de zona de albercas por mantenimiento.")

        # Comprobamos que se despacharon exactamente 2 correos (uno para cada afectado directo)
        self.assertEqual(len(mail.outbox), 2)
        
        destinatarios = [correo.to[0] for correo in mail.outbox]
        self.assertIn('pablo@ciencias.unam.mx', destinatarios)
        self.assertIn('Mario@ciencias.unam.mx', destinatarios)
        
        # Validamos que el asunto sea el correcto para todos los correos del lote
        for correo in mail.outbox:
            self.assertIn('Actualización de parque — Festival de las Luciérnagas', correo.subject)