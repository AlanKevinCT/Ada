from django.test import TestCase, Client
from django.urls import reverse
from datetime import date, time
from ...models import Usuario, Parque, Reservacion

class TestVistasAdministracionReal(TestCase):

    def setUp(self):
        """Configuración del entorno para simulación de peticiones HTTP de administración."""
        self.client = Client()

        self.usuario_cliente = Usuario.objects.create_user(
            correo_electronico='pablo@ciencias.unam.mx',
            nombre='Pablo',
            apellido_paterno='González',
            apellido_materno='Martínez',
            password='123456Contraseña'
        )
        self.usuario_cliente.is_admin = False
        self.usuario_cliente.save()

        self.usuario_admin = Usuario.objects.create_user(
            correo_electronico='admin@ciencias.unam.mx',
            nombre='Gerardo',
            apellido_paterno='Angel',
            apellido_materno='Silva',
            password='adminPassword123'
        )
        self.usuario_admin.is_admin = True
        self.usuario_admin.save()

        self.parque = Parque.objects.create(
            nombre='Parque Bicentenario',
            direccion='Ciudad de México, México',
            servicios='Camping',
            horario_apertura=time(8, 0),
            horario_cierre=time(17, 0),
            capacidad=50,
            activo=True
        )

        # Mapeo de nombres de URLs para facilitar las pruebas
        self.url_panel = reverse('panel_admin')
        self.url_consultar = reverse('consultar_reservas')
        self.url_crear = reverse('crear_parque')
        self.url_editar = reverse('editar_parque', kwargs={'id': self.parque.id})
        self.url_eliminar = reverse('eliminar_parque', kwargs={'id': self.parque.id})

    # ─────────────────────────────────────────────────────────────
    #  1. Panel de Administración
    # ─────────────────────────────────────────────────────────────
    def test_redirige_al_login_si_el_usuario_no_esta_autenticado(self):
        """Prueba para verificar que se redirija al login si el usuario no está autenticado."""
        respuesta = self.client.get(self.url_panel)
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn('login', respuesta.url)

    def test_no_se_renderiza_el_panel_de_administrador_si_el_usuario_no_es_admin(self):
        """Prueba para verificar que no se renderice el panel si el usuario es cliente común."""
        self.client.force_login(self.usuario_cliente)
        respuesta = self.client.get(self.url_panel)
        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(respuesta.url, reverse('inicio'))

    def test_se_renderiza_el_panel_de_administrador_si_el_usuario_es_admin(self):
        """Prueba para verificar que se renderice el panel si el usuario es admin."""
        self.client.force_login(self.usuario_admin)
        respuesta = self.client.get(self.url_panel)
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, 'admin/panel.html')

    # ─────────────────────────────────────────────────────────────
    #  2. Consulta de Reservas con Filtros
    # ─────────────────────────────────────────────────────────────
    def test_consultar_reservas_redirige_a_inicio_si_no_es_admin(self):
        """Verifica restricción de rol en pantalla de consultas."""
        self.client.force_login(self.usuario_cliente)
        respuesta = self.client.get(self.url_consultar)
        self.assertEqual(respuesta.status_code, 302)

    def test_consultar_reservas_renderiza_para_admin_y_trae_datos(self):
        """Verifica renderizado y paso de datos en la consulta filtrada."""
        self.client.force_login(self.usuario_admin)
        respuesta = self.client.get(self.url_consultar)
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn('reservaciones', respuesta.context)

    def test_consultar_reservas_aplica_filtros_correctamente(self):
        """
        Verifica que consultar_reservas muestre todas las reservaciones correctamente 
        aplicando los filtros correspondientes (fecha, parque, tipo de estancia, usuario).
        """
        self.client.force_login(self.usuario_admin)

        parque_extra = Parque.objects.create(
            nombre='Santuario El Rosario', direccion='Michoacán', servicios='Guías',
            horario_apertura=time(9,0), horario_cierre=time(18,0), capacidad=100, activo=True
        )
        usuario_extra = Usuario.objects.create_user(
            correo_electronico='alberto@ciencias.unam.mx', nombre='Alberto',
            apellido_paterno='Nolgos', apellido_materno='Cervantes', password='password456'
        )

        reserva_pablo = Reservacion.objects.create(
            usuario=self.usuario_cliente, parque=self.parque,
            fecha_inicio=date(2026, 6, 10), fecha_fin=date(2026, 6, 12),
            numero_personas=4, tipo_visita='cabana'
        )
        reserva_alberto = Reservacion.objects.create(
            usuario=usuario_extra, parque=parque_extra,
            fecha_inicio=date(2026, 7, 20), fecha_fin=date(2026, 7, 22),
            numero_personas=2, tipo_visita='camping'
        )

        # Filtrado por parque
        respuesta_parque = self.client.get(self.url_consultar, {'parque': self.parque.id})
        self.assertIn(reserva_pablo, respuesta_parque.context['reservaciones'])
        self.assertNotIn(reserva_alberto, respuesta_parque.context['reservaciones'])

        # Filtrado por tipo de visita
        respuesta_tipo = self.client.get(self.url_consultar, {'tipo_estancia': 'cabana'})
        self.assertIn(reserva_pablo, respuesta_tipo.context['reservaciones'])
        self.assertNotIn(reserva_alberto, respuesta_tipo.context['reservaciones'])

        # Filtrado por fecha
        respuesta_fecha = self.client.get(self.url_consultar, {'fecha': '2026-07-20'})
        self.assertIn(reserva_alberto, respuesta_fecha.context['reservaciones'])
        self.assertNotIn(reserva_pablo, respuesta_fecha.context['reservaciones'])

    # ─────────────────────────────────────────────────────────────
    #  3. Creacion de parques
    # ─────────────────────────────────────────────────────────────
    def test_crear_parque_redirige_a_inicio_si_no_es_admin(self):
        """Verifica protección en la ruta de creación."""
        self.client.force_login(self.usuario_cliente)
        respuesta = self.client.get(self.url_crear)
        self.assertEqual(respuesta.status_code, 302)

    def test_crear_parque_renderiza_para_admin(self):
        """Verifica acceso exitoso al HTML de creación."""
        self.client.force_login(self.usuario_admin)
        respuesta = self.client.get(self.url_crear)
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, 'admin/crear_parque.html')

    def test_crear_parque(self):
        """
        Verifica que se cree un nuevo parque correctamente al enviar el formulario 
        de crear_parque con datos válidos.
        """
        self.client.force_login(self.usuario_admin)

        conteo_inicial = Parque.objects.count()

        datos_formulario = {
            'nombre': 'Parque Tlalpan',
            'direccion': 'Tlalpan, CDMX',
            'servicios': 'Caminatas, Bosque',
            'horario_apertura': time(6, 0),
            'horario_cierre': time(16, 0),
            'capacidad': 80,
            'tiene_cabanas': False,
            'tiene_camping': True,
            'tiene_banos': True,
            'tiene_cafeterias': False,
            'tiene_guias': False,
            'tiene_danza': False,
            'tiene_musica': False,
            'tiene_teatro': False,
            'tiene_transporte': False,
            'latitud': 19.2844,
            'longitud': -99.1921
        }

        respuesta = self.client.post(self.url_crear, data=datos_formulario)

        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(respuesta.url, self.url_panel)
        
        self.assertEqual(Parque.objects.count(), conteo_inicial + 1)
        self.assertTrue(Parque.objects.filter(nombre='Parque Tlalpan').exists())
    

    # ─────────────────────────────────────────────────────────────
    #  4. Edición de parques
    # ─────────────────────────────────────────────────────────────
    def test_editar_parque_redirige_a_inicio_si_no_es_admin(self):
        """Verifica protección en la ruta de edición."""
        self.client.force_login(self.usuario_cliente)
        respuesta = self.client.get(self.url_editar)
        self.assertEqual(respuesta.status_code, 302)

    def test_editar_parque_renderiza_para_admin(self):
        """Verifica paso de contexto del parque seleccionado en edición."""
        self.client.force_login(self.usuario_admin)
        respuesta = self.client.get(self.url_editar)
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.context['parque'], self.parque)

    def test_editar_parque(self):
        """
        Verifica que se edite un parque correctamente al enviar el formulario 
        de editar_parque con datos válidos.
        """
        self.client.force_login(self.usuario_admin)

        datos_edicion = {
            'nombre': 'Parque Bicentenario MODIFICADO',
            'direccion': 'Nueva Dirección, CDMX',
            'servicios': 'Camping y zona VIP',
            'horario_apertura': '08:00',
            'horario_cierre': '19:00', # Cambió de 17:00 a 19:00
            'capacidad': 120,          # Cambió de 50 a 120
            'tiene_cabanas': True,
            'tiene_banos': True,
            'tiene_cafeterias': True,
            'tiene_danza': True,
            'latitud': 19.5855,
            'longitud': -100.2831
        }

        respuesta = self.client.post(self.url_editar, data=datos_edicion)

        # Debe redirigir al guardar
        self.assertEqual(respuesta.status_code, 302)

        self.parque.refresh_from_db()
        self.assertEqual(self.parque.nombre, 'Parque Bicentenario MODIFICADO')
        self.assertEqual(self.parque.capacidad, 120)
        self.assertEqual(self.parque.horario_cierre, time(19, 0))

    # ─────────────────────────────────────────────────────────────
    #  5. Eliminación de parques
    # ─────────────────────────────────────────────────────────────
    def test_eliminar_parque_redirige_a_inicio_si_no_es_admin(self):
        """Verifica protección en la ruta de eliminación."""
        self.client.force_login(self.usuario_cliente)
        respuesta = self.client.get(self.url_eliminar)
        self.assertEqual(respuesta.status_code, 302)

    def test_eliminar_parque(self):
        """Un POST válido debe invocar la lógica, borrar el parque de la BD y redirigir."""
        self.client.force_login(self.usuario_admin)
        
        respuesta = self.client.post(self.url_eliminar)
        
        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(respuesta.url, self.url_panel)
        self.assertFalse(Parque.objects.filter(id=self.parque.id).exists())