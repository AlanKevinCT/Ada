from django.test import TestCase, Client
from django.urls import reverse
from ...models import Usuario

class TestVistasAutenticacionReal(TestCase):

    def setUp(self):
        """Configuración del cliente HTTP y persistencia real de usuarios."""
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

        # Mapeo de rutas para facilitar las pruebas
        self.url_inicio = reverse('inicio')
        self.url_registro = reverse('registro')
        self.url_login = reverse('login')
        self.url_logout = reverse('logout')

    # ─────────────────────────────────────────────────────────────
    #  1. Inicio de Mapa sin Autenticación
    # ─────────────────────────────────────────────────────────────
    def test_renderizacion_correcta_del_mapa_sin_autenticacion(self):
        """Prueba para la renderización correcta del mapa sin autenticación."""
        respuesta = self.client.get(self.url_inicio)
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, 'mapa/mapa.html')
        self.assertIn('geojson', respuesta.context)
        self.assertIn('parques', respuesta.context)

    # ─────────────────────────────────────────────────────────────
    #  2. Registro
    # ─────────────────────────────────────────────────────────────
    def test_registro_de_un_nuevo_usuario(self):
        """Prueba para el registro exitoso de un nuevo usuario cliente."""
        datos_post = {
            'correo_electronico': 'nuevo_usuario@ciencias.unam.mx',
            'nombre': 'Alberto',
            'apellido_paterno': 'Nolgos',
            'apellido_materno': 'Cervantes',
            'password': 'AlbertoNolgos2026!', 
            'confirmar_password': 'AlbertoNolgos2026!'
        }
        respuesta = self.client.post(self.url_registro, data=datos_post)
        
        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(respuesta.url, self.url_inicio)
        
        # Validamos que de verdad exista en la base de datos de pruebas
        self.assertTrue(Usuario.objects.filter(correo_electronico='nuevo_usuario@ciencias.unam.mx').exists())

    def test_registro_usuario_que_ya_existe(self):
        """Prueba para intentar registrar un correo que ya fue registrado."""
        datos_duplicados = {
            'correo_electronico': 'pablo@ciencias.unam.mx',
            'nombre': 'Pablo Duplicado',
            'apellido_paterno': 'González',
            'apellido_materno': 'Martínez',
            'password': 'otraContraseña',
            'confirmar_password': 'otraContraseña'
        }
        respuesta = self.client.post(self.url_registro, data=datos_duplicados)
        
        # Al fallar la validación del form, no debe redirigir, vuelve a pintar con HTTP 200.
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, 'registro.html')

    # ─────────────────────────────────────────────────────────────
    #  3. Inicio de Sesión (def login)
    # ─────────────────────────────────────────────────────────────
    def test_inicio_de_sesion_con_credenciales_correctas(self):
        """Prueba para el inicio de sesión exitoso de un cliente."""
        datos_login = {
            'correo_electronico': 'pablo@ciencias.unam.mx',
            'password': '123456Contraseña'
        }
        respuesta = self.client.post(self.url_login, data=datos_login)
        
        # Redirige al mapa de inicio
        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(respuesta.url, self.url_inicio)

    def test_inicio_de_sesion_con_credenciales_incorrectas(self):
        """Prueba para el inicio de sesión con contraseña equivocada."""
        datos_incorrectos = {
            'correo_electronico': 'pablo@ciencias.unam.mx',
            'password': 'password_erroneo'
        }
        respuesta = self.client.post(self.url_login, data=datos_incorrectos)
        
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.context['error'], 'Correo o contraseña incorrectos.')

    def test_inicio_de_sesion_con_usuario_que_no_existe(self):
        """Prueba para el inicio de sesión de un correo fantasma."""
        datos_fantasma = {
            'correo_electronico': 'no_existo@ciencias.unam.mx',
            'password': 'password123'
        }
        respuesta = self.client.post(self.url_login, data=datos_fantasma)
        
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.context['error'], 'Correo o contraseña incorrectos.')

    def test_inicio_de_sesion_de_usuario_administrador(self):
        """Prueba de control de roles: un administrador debe ser redirigido a su panel (def login)."""
        datos_admin = {
            'correo_electronico': 'admin@ciencias.unam.mx',
            'password': 'adminPassword123'
        }
        respuesta = self.client.post(self.url_login, data=datos_admin)
        
        # Ejecuta el redirect hacia el dashboard administrativo
        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(respuesta.url, reverse('panel_admin'))

    # ─────────────────────────────────────────────────────────────
    #  4. Cierre de Sesión
    # ─────────────────────────────────────────────────────────────
    def test_cierre_de_sesion(self):
        """Prueba para el cierre de sesión."""
        self.client.force_login(self.usuario_cliente)
        respuesta = self.client.get(self.url_logout)
        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(respuesta.url, self.url_inicio)