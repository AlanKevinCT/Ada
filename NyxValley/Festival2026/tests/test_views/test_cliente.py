from django.test import TestCase, Client
from django.urls import reverse
from datetime import date, time
from ...models import Usuario, Parque, Reservacion

class TestVistasClienteReal(TestCase):

    def setUp(self):
        """Configuración del cliente HTTP y preparación de datos específicos de perfiles."""
        self.client = Client()

        self.cliente_pablo = Usuario.objects.create_user(
            correo_electronico='pablo@ciencias.unam.mx',
            nombre='Pablo',
            apellido_paterno='González',
            apellido_materno='Martínez',
            password='123456Contraseña'
        )
        self.cliente_pablo.is_admin = False
        self.cliente_pablo.save()

        self.cliente_intruso = Usuario.objects.create_user(
            correo_electronico='intruso@ciencias.unam.mx',
            nombre='Juan',
            apellido_paterno='Pérez',
            apellido_materno='López',
            password='PasswordIntruso123'
        )
        self.cliente_intruso.is_admin = False
        self.cliente_intruso.save()

        self.usuario_admin = Usuario.objects.create_user(
            correo_electronico='admin@ciencias.unam.mx',
            nombre='Manuel',
            apellido_paterno='Angel',
            apellido_materno='Silva',
            password='adminPassword123'
        )
        self.usuario_admin.is_admin = True
        self.usuario_admin.save()

        self.parque = Parque.objects.create(
            nombre='Parque Bicentenario', direccion='CDMX', servicios='Camping',
            horario_apertura=time(8, 0), horario_cierre=time(17, 0), capacidad=50, activo=True
        )

        self.reserva_pablo = Reservacion.objects.create(
            usuario=self.cliente_pablo, parque=self.parque,
            fecha_inicio=date(2026, 6, 10), fecha_fin=date(2026, 6, 12),
            numero_personas=4, tipo_visita='cabana'
        )

        # Mapeo de URLs
        self.url_panel = reverse('panel_cliente')
        self.url_mis_reservas = reverse('mis_reservaciones')
        self.url_cancelar = reverse('cancelar_reservacion', kwargs={'id': self.reserva_pablo.id})

    # ─────────────────────────────────────────────────────────────
    #  1. Panel Cliente
    # ─────────────────────────────────────────────────────────────
    def test_no_se_renderiza_el_panel_cliente_si_el_cliente_no_esta_logeado(self):
        """Prueba para que no se renderice el panel cliente si el cliente no está logeado."""
        respuesta = self.client.get(self.url_panel)
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn('login', respuesta.url)

    def test_no_se_renderiza_el_panel_cliente_si_es_admin(self):
        """Prueba de aislamiento de roles: Bloquea al administrador del panel de clientes."""
        self.client.force_login(self.usuario_admin)
        respuesta = self.client.get(self.url_panel)
        
        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(respuesta.url, reverse('inicio'))

    def test_se_renderiza_el_panel_cliente_exitosamente(self):
        """Prueba para que se renderice el panel cliente con un usuario autenticado común."""
        self.client.force_login(self.cliente_pablo)
        respuesta = self.client.get(self.url_panel)
        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(respuesta.url, reverse('inicio'))

    # ─────────────────────────────────────────────────────────────
    #  2. Lista de Reservaciones
    # ─────────────────────────────────────────────────────────────
    def test_no_se_renderiza_las_reservaciones_del_cliente_si_no_esta_logeado(self):
        """Verifica que no se renderice la página de mis_reservaciones si el cliente no está logeado."""
        respuesta = self.client.get(self.url_mis_reservas)
        self.assertEqual(respuesta.status_code, 302)

    def test_se_renderiza_las_reservaciones_del_cliente_autenticado(self):
        """Prueba para que se renderice la página de mis_reservaciones de forma correcta."""
        self.client.force_login(self.cliente_pablo)
        respuesta = self.client.get(self.url_mis_reservas)
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, 'cliente/mis_reservaciones.html')

    def test_mis_reservaciones_filtra_estricto_y_oculta_datos_ajenos(self):
        """Verifica que un cliente no vea las reservaciones de otros usuarios."""
        # Creamos una reserva que le pertenece a otro usuario para asegurarnos de que no se muestre en el listado de Pablo
        reserva_ajena = Reservacion.objects.create(
            usuario=self.cliente_intruso, parque=self.parque,
            fecha_inicio=date(2026, 7, 15), fecha_fin=date(2026, 7, 18),
            numero_personas=2, tipo_visita='camping'
        )
        
        self.client.force_login(self.cliente_pablo)
        respuesta = self.client.get(self.url_mis_reservas)
        
        # En el contexto solo debe figurar la reserva de Pablo
        reservas_visibles = respuesta.context['reservaciones']
        self.assertIn(self.reserva_pablo, reservas_visibles)
        self.assertNotIn(reserva_ajena, reservas_visibles)

    # ─────────────────────────────────────────────────────────────
    #  3. Cancelación de Reservaciones
    # ─────────────────────────────────────────────────────────────
    def test_no_se_cancele_una_reservacion_si_no_esta_logeado(self):
        """Verifica que un usuario anónimo no pueda cancelar reservaciones si no está logeado."""
        respuesta = self.client.post(self.url_cancelar)
        self.assertEqual(respuesta.status_code, 302)
        self.reserva_pablo.refresh_from_db()
        self.assertEqual(self.reserva_pablo.estado, 'activa')

    def test_cancelar_una_reservacion(self):
        """Prueba para que se cancele una reservación si el dueño legítimo manda el POST."""
        self.client.force_login(self.cliente_pablo)
        
        respuesta = self.client.post(self.url_cancelar)
        
        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(respuesta.url, self.url_mis_reservas)
        
        self.reserva_pablo.refresh_from_db()
        self.assertEqual(self.reserva_pablo.estado, 'cancelada')

    def test_bloqueo_de_intromision_entre_clientes_al_cancelar(self):
        """Verifica que se bloqueen intentos de alterar reservas ajenas."""
        self.client.force_login(self.cliente_intruso)
        respuesta = self.client.post(self.url_cancelar)
        
        self.assertEqual(respuesta.status_code, 404)
        
        self.reserva_pablo.refresh_from_db()
        self.assertEqual(self.reserva_pablo.estado, 'activa')