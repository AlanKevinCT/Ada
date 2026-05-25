from django.test import TestCase, Client
from django.urls import reverse
from datetime import date, time
from ...models import Usuario, Parque, Reservacion

class TestReservacionesControlador(TestCase):

    def setUp(self):
        self.client = Client()
        
        self.usuario = Usuario.objects.create_user(
            correo_electronico='pablo@ciencias.unam.mx',
            nombre='Pablo',
            apellido_paterno='Hernández',
            apellido_materno='García',
            password='PasswordFuerte123!'
        )
        
        self.parque = Parque.objects.create(
            nombre='Parque Bicentenario',
            direccion='CDMX',
            horario_apertura=time(9, 0),
            horario_cierre=time(18, 0),
            capacidad=200,
            activo=True,
            tiene_camping=True,
            tiene_cabanas=False
        )
        
        # URLs de las vistas
        self.url_reserva = reverse('formulario_reserva')
        self.url_confirmacion = reverse('confirmacion')

    # ─────────────────────────────────────────────────────────────
    #  1. Pruebas de Acceso y Autenticación
    # ─────────────────────────────────────────────────────────────
    def test_formulario_reserva_usuario_anonimo(self):
        """Verifica que un usuario no autenticado sea rebotado al intentar acceder al formulario."""
        respuesta = self.client.get(self.url_reserva)
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn('/login/', respuesta.url)

    def test_confirmacion_anonimo_redirige_al_login(self):
        """Verifica que un usuario no autenticado no pueda ver confirmaciones."""
        respuesta = self.client.get(self.url_confirmacion)
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn('/login/', respuesta.url)

    # ─────────────────────────────────────────────────────────────
    #  2. Formulario de Reserva
    # ─────────────────────────────────────────────────────────────
    def test_renderizacion_formulario_reserva(self):
        """Verifica que un usuario logueado pueda ver la interfaz de reservación con sus campos."""
        self.client.login(correo_electronico='pablo@ciencias.unam.mx', password='PasswordFuerte123!')
        respuesta = self.client.get(self.url_reserva)
        
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, 'cliente/formulario_reserva.html')
        self.assertIn('form', respuesta.context)
        self.assertIn('parques', respuesta.context)

    def test_reserva_exitosa(self):
        """Verifica el flujo correcto (POST): guarda en base de datos, asigna sesión y redirige."""
        self.client.login(correo_electronico='pablo@ciencias.unam.mx', password='PasswordFuerte123!')
        
        datos_post = {
            'parque': self.parque.id,
            'fecha_inicio': date(2026, 6, 18),
            'fecha_fin': date(2026, 6, 20),
            'numero_personas': 3,
            'tipo_visita': 'camping'
        }
        
        respuesta = self.client.post(self.url_reserva, data=datos_post)
        
        self.assertEqual(respuesta.status_code, 302)
        self.assertRedirects(respuesta, self.url_confirmacion)
        self.assertTrue(Reservacion.objects.filter(usuario=self.usuario, parque=self.parque).exists())
        
        reservacion_reciente = Reservacion.objects.get(usuario=self.usuario, parque=self.parque)
        self.assertEqual(self.client.session['ultima_reservacion_id'], reservacion_reciente.id)

    def test_reserva_fallida(self):
        """Verifica que se arroje un error al enviar datos inválidos."""
        self.client.login(correo_electronico='pablo@ciencias.unam.mx', password='PasswordFuerte123!')
        
        datos_erroneos = {
            'parque': self.parque.id,
            'fecha_inicio': date(2026, 6, 18),
            'fecha_fin': date(2026, 6, 20),
            'numero_personas': 0,
            'tipo_visita': 'camping'
        }
        
        respuesta = self.client.post(self.url_reserva, data=datos_erroneos)
        
        self.assertEqual(respuesta.status_code, 200)
        form = respuesta.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('numero_personas', form.errors)

    def test_reserva_atrapa_excepcion_del_servicio_value_error(self):
        """Verifica que el formulario arroje un error no asociado a un campo específico cuando el servicio levanta un ValueError."""
        self.client.login(correo_electronico='pablo@ciencias.unam.mx', password='PasswordFuerte123!')
        
        datos_conflicto = {
            'parque': self.parque.id,
            'fecha_inicio': date(2026, 6, 18),
            'fecha_fin': date(2026, 6, 20),
            'numero_personas': 4,
            'tipo_visita': 'cabana'
        }
        
        respuesta = self.client.post(self.url_reserva, data=datos_conflicto)
        
        self.assertEqual(respuesta.status_code, 200)
        form = respuesta.context['form']
        self.assertTrue(len(form.non_field_errors()) > 0)

    # ─────────────────────────────────────────────────────────────
    #  3. Página de Confirmación
    # ─────────────────────────────────────────────────────────────
    def test_confirmacion_con_datos_de_sesion_validos(self):
        """Verifica que la confirmación muestre los datos correctos cuando la sesión contiene un id válido."""
        self.client.login(correo_electronico='pablo@ciencias.unam.mx', password='PasswordFuerte123!')
        
        reserva = Reservacion.objects.create(
            usuario=self.usuario,
            parque=self.parque,
            fecha_inicio=date(2026, 6, 18),
            fecha_fin=date(2026, 6, 20),
            numero_personas=2,
            tipo_visita='camping'
        )
        
        sesion = self.client.session
        sesion['ultima_reservacion_id'] = reserva.id
        sesion.save()
        
        respuesta = self.client.get(self.url_confirmacion)
        
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, 'cliente/confirmacion.html')
        self.assertEqual(respuesta.context['reservacion'], reserva)

    def test_confirmacion_limpia_sesion_tras_primer_consumo_y_f5_falla(self):
        """Verifica que tras renderizar una vez, al recargar la página ya no muestre los datos."""
        self.client.login(correo_electronico='pablo@ciencias.unam.mx', password='PasswordFuerte123!')
        
        reserva = Reservacion.objects.create(
            usuario=self.usuario,
            parque=self.parque,
            fecha_inicio=date(2026, 6, 18),
            fecha_fin=date(2026, 6, 20),
            numero_personas=2,
            tipo_visita='camping'
        )
        
        sesion = self.client.session
        sesion['ultima_reservacion_id'] = reserva.id
        sesion.save()
        
        self.client.get(self.url_confirmacion)
        
        respuesta_f5 = self.client.get(self.url_confirmacion)
        
        self.assertEqual(respuesta_f5.status_code, 200)
        self.assertIsNone(respuesta_f5.context['reservacion'])