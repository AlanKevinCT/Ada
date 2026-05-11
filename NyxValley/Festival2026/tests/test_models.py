from django.db import IntegrityError
from django.test import TestCase
from ..models import Usuario, Parque, Reservacion
from datetime import date

class TestModelosFestival(TestCase):

    def setUp(self):
        """Configuración de datos iniciales para las pruebas."""
        # Creamos un usuario de prueba
        self.usuario = Usuario.objects.create_user(
            correo_electronico='pablo@ciencias.unam.mx',
            nombre='Pablo',
            apellido_paterno='González',
            apellido_materno='Martínez',
            password='123456Contraseña'
        )

        # Creamos un parque de prueba
        self.parque = Parque.objects.create(
            nombre='Parque Bicentenario',
            direccion='Ciudad de México, México',
            servicios='Camping, comida',
            horario='08:00 - 17:00',
            capacidad=50,
            tiene_cabanas=True,
            latitud=19.5855,
            longitud=-100.2831
        )

        self.reservacion = Reservacion.objects.create(
            usuario=self.usuario,
            parque=self.parque,
            fecha_inicio=date(2026, 6, 10),
            fecha_fin=date(2026, 6, 12),
            numero_personas=4,
            tipo_visita='cabana'
        )


    # ─────────────────────────────────────────────────────────────
    #  Pruebas para el modelo Usuario (RF-02, RNF-06)
    # ─────────────────────────────────────────────────────────────
    def test_creacion_usuario(self):
        """Verifica que el usuario se cree correctamente."""
        self.assertEqual(self.usuario.correo_electronico, 'pablo@ciencias.unam.mx')
        self.assertEqual(self.usuario.nombre_completo(), 'Pablo González Martínez')
        self.assertTrue(self.usuario.is_active)
        # Verificar que la contraseña no se guarde en texto plano (RNF-06)
        self.assertNotEqual(self.usuario.password, '123456Contraseña')

    def test_error_correo_duplicado(self):
        """
        Verifica que el sistema impida crear dos usuarios con el mismo correo.
        """
        # Intentamos crear un segundo usuario con el mismo correo que 'self.usuario'
        with self.assertRaises(IntegrityError):
            Usuario.objects.create_user(
                correo_electronico='pablo@ciencias.unam.mx', # Es el que está en setUp
                nombre='Usuario Duplicado',
                apellido_paterno='Usuario',
                apellido_materno='Prueba',
                password='otraContraseña'
            )

    def test_exito_correo_diferente(self):
        """Verifica que se puedan crear múltiples usuarios si los correos son distintos."""
        nuevo_usuario = Usuario.objects.create_user(
            correo_electronico='Alberto@ciencias.unam.mx', # Correo diferente
            nombre='Alberto Gabriel',
            apellido_paterno='Nolgos',
            apellido_materno='Cervantes',
            password='password456'
        )
        self.assertEqual(Usuario.objects.count(), 2) # Ya deben haber dos usuarios en total
        self.assertEqual(nuevo_usuario.nombre, 'Alberto Gabriel')

    # ─────────────────────────────────────────────────────────────
    #  Pruebas para el modelo Parque
    # ─────────────────────────────────────────────────────────────
    def test_creacion_parque(self):
        """Verifica los atributos del parque y valores por defecto."""
        self.assertEqual(self.parque.nombre, 'Parque Bicentenario')
        self.assertTrue(self.parque.tiene_camping)
        self.assertTrue(self.parque.activo)
        self.assertEqual(self.parque.latitud, 19.5855)
        self.assertEqual(self.parque.longitud, -100.2831)

    # ─────────────────────────────────────────────────────────────
    #  Pruebas para el modelo Reservacion (RF-10)
    # ─────────────────────────────────────────────────────────────
    def test_creacion_reservacion(self):
        """Verifica que la reservación se vincule correctamente al usuario y parque."""
        self.assertEqual(self.reservacion.estado, 'activa')
        self.assertEqual(self.reservacion.duracion_dias(), 2)
        self.assertEqual(self.reservacion.tipo_visita, 'cabana')

    def test_borrado_en_cascada_usuario(self):
        """Verifica que al eliminar un usuario se eliminen sus reservaciones (Cascada)."""
        self.assertEqual(Reservacion.objects.count(), 1) # Hay una reservación creada en setUp
        self.usuario.delete()
        self.assertEqual(Reservacion.objects.count(), 0)

    def test_str_reservacion(self):
        """Prueba el método __str__ de la reservación."""
        # El formato esperado según el modelo
        esperado = 'Reservación de Pablo en Parque Bicentenario (2026-06-10 → 2026-06-12)'
        self.assertEqual(str(self.reservacion), esperado)