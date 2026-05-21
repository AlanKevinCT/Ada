from django.test import TestCase
from datetime import date
from ..models import Usuario, Parque
from ..forms import RegistroForm, LoginForm, ReservaForm

class TestFormulariosFestival(TestCase):

    def setUp(self):
        """Configuración de datos base para las pruebas de los formularios."""
        self.usuario_existente = Usuario.objects.create_user(
            correo_electronico='aldo@ciencias.unam.mx',
            nombre='Aldo',
            apellido_paterno='García',
            apellido_materno='Martínez',
            password='password123'
        )

        # Parque 1: SÍ tiene cabañas
        self.parque_con_cabanas = Parque.objects.create(
            nombre='Parque Con Cabañas',
            capacidad=50,
            tiene_cabanas=True,
            activo=True
        )

        # Parque 2: NO tiene cabañas (Solo camping)
        self.parque_sin_cabanas = Parque.objects.create(
            nombre='Parque Solo Camping',
            capacidad=50,
            tiene_cabanas=False,
            activo=True
        )

    # ─────────────────────────────────────────────────────────────
    #  1. Pruebas para RegistroForm
    # ─────────────────────────────────────────────────────────────
    def test_registro_form_datos_validos(self):
        """Verifica que el formulario sea válido con datos correctos."""
        datos = {
            'correo_electronico': 'nuevo_usuario@gmail.com',
            'nombre': 'Paco',
            'apellido_paterno': 'Pérez',
            'apellido_materno': 'López',
            'password': 'contraseña_segura',
            'confirmar_password': 'contraseña_segura'
        }
        form = RegistroForm(data=datos)
        self.assertTrue(form.is_valid())

    def test_registro_form_contraseñas_no_coinciden(self):
        """Verifica que el formulario detecte si las contraseñas no son iguales."""
        
        # Contraseñas no coinciden
        datos = {
            'correo_electronico': 'paco@gmail.com',
            'nombre': 'Paco',
            'apellido_paterno': 'Pérez',
            'password': 'password_1',
            'confirmar_password': 'password_2'
        }
        form = RegistroForm(data=datos)
        self.assertFalse(form.is_valid())
        self.assertIn('Las contraseñas no coinciden.', form.non_field_errors())
    
    def test_registro_form_correo_ya_registrado(self):
        """Verifica que el formulario impida registrar un correo que ya existe."""
        #  Correo ya registrado
        datos = {
            'correo_electronico': 'aldo@ciencias.unam.mx',
            'nombre': 'Aldo',
            'apellido_paterno': 'García',
            'password': 'password123',
            'confirmar_password': 'password123'
        }
        form = RegistroForm(data=datos)
        self.assertFalse(form.is_valid())
        self.assertIn('Este correo ya está registrado.', form.errors['correo_electronico'])
    
    def test_registro_form_campos_obligatorios_vacios(self):
        """Verifica que el formulario sea inválido si faltan los datos obligatorios."""
        # Enviamos un diccionario completamente vacío
        form = RegistroForm(data={})
        
        self.assertFalse(form.is_valid())
        
        # Verificamos que cada campo obligatorio tenga un error de validación
        self.assertIn('correo_electronico', form.errors)
        self.assertIn('nombre', form.errors)
        self.assertIn('apellido_paterno', form.errors)
        self.assertIn('password', form.errors)
        self.assertIn('confirmar_password', form.errors)
        
        self.assertIn('Este campo es obligatorio.', form.errors['nombre'])

    def test_registro_form_formato_correo_invalido(self):
        """Verifica que se rechacen cadenas de texto que no cumplan el formato de email."""
        datos = {
            'correo_electronico': 'correo_falso_sin_arroba',
            'nombre': 'Paco',
            'apellido_paterno': 'Pérez',
            'password': 'contraseña_segura',
            'confirmar_password': 'contraseña_segura'
        }
        form = RegistroForm(data=datos)
        
        self.assertFalse(form.is_valid())
        self.assertIn('correo_electronico', form.errors)
        self.assertIn('Introduzca una dirección de correo válida.', form.errors['correo_electronico'])

    def test_registro_form_espacios_en_blanco(self):
        """Verifica que el formulario no acepte espacios en blanco como caracteres válidos."""
        datos = {
            'correo_electronico': 'paco@gmail.com',
            'nombre': '   ',
            'apellido_paterno': 'Pérez',
            'password': 'contraseña_segura',
            'confirmar_password': 'contraseña_segura'
        }
        form = RegistroForm(data=datos)
        
        self.assertFalse(form.is_valid())
        self.assertIn('nombre', form.errors)
        self.assertIn('Este campo es obligatorio.', form.errors['nombre'])

    # ─────────────────────────────────────────────────────────────
    #  2. Pruebas para LoginForm
    # ─────────────────────────────────────────────────────────────
    def test_login_form_datos_validos(self):
        """Verifica que el formulario de login sea válido con credenciales bien estructuradas."""
        datos = {
            'correo_electronico': 'aldo@ciencias.unam.mx',
            'password': 'password123'
        }
        form = LoginForm(data=datos)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['correo_electronico'], 'aldo@ciencias.unam.mx')
        self.assertEqual(form.cleaned_data['password'], 'password123')

    def test_login_form_campos_obligatorios_vacios(self):
        """Verifica que el login falle si el usuario no proporciona el correo o la contraseña."""
        form = LoginForm(data={})
        self.assertFalse(form.is_valid())
        
        # Ambos campos deben exigir datos por defecto
        self.assertIn('correo_electronico', form.errors)
        self.assertIn('password', form.errors)
        self.assertIn('Este campo es obligatorio.', form.errors['password'])

    def test_login_form_correo_invalido(self):
        """Verifica que el formulario rechace el login si el formato del email está roto."""
        datos = {
            'correo_electronico': 'usuario_sin_formato_email',
            'password': 'password123'
        }
        form = LoginForm(data=datos)
        self.assertFalse(form.is_valid())
        self.assertIn('correo_electronico', form.errors)
        self.assertIn('Introduzca una dirección de correo válida.', form.errors['correo_electronico'])