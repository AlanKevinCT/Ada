from django.test import TestCase
from datetime import date, time
from ..models import Usuario, Parque
from ..forms import RegistroForm, LoginForm, ReservaForm, ParqueForm

class TestFormulariosFestival(TestCase):

    def setUp(self):
        """Configuración de datos base para las pruebas de los formularios."""
        self.usuario_existente = Usuario.objects.create_user(
            correo_electronico='aldo@ciencias.unam.mx',
            nombre='Aldo',
            apellido_paterno='García',
            apellido_materno='Martínez',
            password='AldoGarcia2026!'
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
            'password': 'PacoPerez2026!', 
            'confirmar_password': 'PacoPerez2026!'
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
            'password': 'PasswordFuerte123!',
            'confirmar_password': 'PasswordDiferente123!'
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
            'password': 'AldoGarcia2026!',
            'confirmar_password': 'AldoGarcia2026!'
        }
        form = RegistroForm(data=datos)
        self.assertFalse(form.is_valid())
        self.assertIn('No fue posible completar el registro. Verifica tus datos.', form.errors['correo_electronico'])
    
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
            'password': 'ContraseñaSegura2026!',
            'confirmar_password': 'ContraseñaSegura2026!'
        }
        form = RegistroForm(data=datos)
        
        self.assertFalse(form.is_valid())
        self.assertIn('correo_electronico', form.errors)
        self.assertIn('Introduzca una dirección de correo electrónico válida.', form.errors['correo_electronico'])

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
            'password': 'AldoGarcia2026!'
        }
        form = LoginForm(data=datos)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['correo_electronico'], 'aldo@ciencias.unam.mx')
        self.assertEqual(form.cleaned_data['password'], 'AldoGarcia2026!')

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
            'password': 'AldoGarcia2026!'
        }
        form = LoginForm(data=datos)
        self.assertFalse(form.is_valid())
        self.assertIn('correo_electronico', form.errors)
        self.assertIn('Introduzca una dirección de correo electrónico válida.', form.errors['correo_electronico'])

    # ─────────────────────────────────────────────────────────────
    #  3. Pruebas para ReservaForm
    # ─────────────────────────────────────────────────────────────
    def test_reserva_form_datos_validos(self):
        """Verifica que el formulario sea válido con un flujo de datos correcto."""
        datos = {
            'parque': self.parque_con_cabanas.id,
            'fecha_inicio': date(2026, 6, 18),  # Jueves
            'fecha_fin': date(2026, 6, 20),     # Sabado
            'numero_personas': 4,
            'tipo_visita': 'cabana'
        }
        form = ReservaForm(data=datos)
        self.assertTrue(form.is_valid())

    def test_reserva_form_fechas_invalidas_festival(self):
        """Verifica que clean() atrape rangos prohibidos (Martes intermedio)."""
        datos = {
            'parque': self.parque_con_cabanas.id,
            'fecha_inicio': date(2026, 6, 15),  # Lunes
            'fecha_fin': date(2026, 6, 18),     # Contiene el martes 16 en medio
            'numero_personas': 2,
            'tipo_visita': 'camping'
        }
        form = ReservaForm(data=datos)
        self.assertFalse(form.is_valid())
        self.assertIn(
            'La fecha no es válida porque incluye un martes, y ese día no se puede reservar.', 
            form.non_field_errors()
        )

    def test_reserva_form_bloqueo_cabanas_en_parque_sin_ellas(self):
        """Verifica que el formulario impida reservar una cabaña si la instancia específica del parque no cuenta con ese servicio."""
        datos = {
            'parque': self.parque_sin_cabanas.id,
            'fecha_inicio': date(2026, 6, 24),
            'fecha_fin': date(2026, 6, 26),
            'numero_personas': 2,
            'tipo_visita': 'cabana'
        }
        form = ReservaForm(data=datos)
        
        self.assertFalse(form.is_valid(), "El formulario ignoró que el parque no tiene cabañas por el bug de la P mayúscula en linea 99 del archivo forms.py.")
        
        if not form.is_valid():
            self.assertTrue(any('no cuenta con cabañas' in error for error in form.non_field_errors()))

    def test_reserva_form_sin_disponibilidad_cupo(self):
        """Verifica que clean() rebote la solicitud si el servicio reporta sobrecupo."""
        # Modificamos temporalmente la capacidad del parque para simular sobrecupo inmediato
        self.parque_con_cabanas.capacidad = 0
        self.parque_con_cabanas.save()

        datos = {
            'parque': self.parque_con_cabanas.id,
            'fecha_inicio': date(2026, 6, 24),
            'fecha_fin': date(2026, 6, 26),
            'numero_personas': 2,
            'tipo_visita': 'cabana'
        }
        form = ReservaForm(data=datos)
        self.assertFalse(form.is_valid())
        self.assertIn('No hay disponibilidad en el parque para esas fechas.', form.non_field_errors())

    def test_reserva_form_numero_personas_negativo(self):
        """Verifica que el validador nativo min_value=1 bloquee registros de 0 o menos personas."""
        datos = {
            'parque': self.parque_con_cabanas.id,
            'fecha_inicio': date(2026, 6, 24),
            'fecha_fin': date(2026, 6, 26),
            'numero_personas': 0,
            'tipo_visita': 'camping'
        }
        form = ReservaForm(data=datos)
        self.assertFalse(form.is_valid())
        self.assertIn('numero_personas', form.errors)
        self.assertIn('Asegúrese de que este valor sea mayor o igual a 1.', form.errors['numero_personas'])