from django.test import TestCase
from ..decorators import ParqueBase, Cabanas, ServicioParqueDecorator

class TestPatronDecoratorParques(TestCase):

    def setUp(self):
        """Configuración de un parque base listo para ser decorado."""
        self.parque_base = ParqueBase(
            nombre="Parque Bicentenario",
            direccion="CDMX, México",
            horario="08:00 - 17:00"
        )

    # ─────────────────────────────────────────────────────────────
    #  1. Pruebas para el Componente Base
    # ─────────────────────────────────────────────────────────────
    def test_parque_base_retorna_datos_correctos(self):
        """Verifica que el parque base devuelva sus datos iniciales sin alteraciones."""
        self.assertEqual(self.parque_base.getNombre(), "Parque Bicentenario")
        self.assertEqual(self.parque_base.getDireccion(), "CDMX, México")
        self.assertEqual(self.parque_base.getHorario(), "08:00 - 17:00")
        self.assertIn("Zona de camping incluida", str(self.parque_base))

    # ─────────────────────────────────────────────────────────────
    #  2. Pruebas para los Decoradores
    # ─────────────────────────────────────────────────────────────
    def test_decorador_cabanas_extiende_el_nombre(self):
        """Verifica que el decorador de cabañas añada correctamente sus atributos al nombre."""
        parque_con_cabanas = Cabanas(
            servicio=self.parque_base,
            tipo="familiar",
            capacidad=6
        )
        # Debe conservar el nombre base y anexar el servicio del decorador
        self.assertEqual(parque_con_cabanas.getNombre(), "Parque Bicentenario (+ Cabañas familiar)")
        self.assertIn("Cabañas tipo familiar, capacidad 6", str(parque_con_cabanas))

    def test_decorador_servicios_modifica_horario_y_permite_actualizaciones(self):
        """Verifica la mutación de estado y el cambio de horario en ServicioParqueDecorator."""
        parque_con_danza = ServicioParqueDecorator(
            servicio=self.parque_base,
            servicio_extra="Clases de Danza",
            horario="18:00 - 20:00",
            capacidad=20
        )
        
        # 1. Verifica que este decorador sobreescribe el horario original
        self.assertEqual(parque_con_danza.getHorario(), "18:00 - 20:00")
        
        # 2. Prueba el método de mutación actualizarParque()
        parque_con_danza.actualizarParque("Taller de Teatro")
        self.assertEqual(parque_con_danza.servicio_extra, "Taller de Teatro")
        self.assertIn("Servicio extra: Taller de Teatro", str(parque_con_danza))

    # ─────────────────────────────────────────────────────────────
    #  3. Decoración Múltiple (Composición)
    # ─────────────────────────────────────────────────────────────
    def test_decoracion_multiple_acumula_servicios(self):
        """Verifica que el patrón acumule dinámicamente múltiples capas de decoradores."""
        # Capa 1: Parque Base
        # Capa 2: Envolvemos con Cabañas
        parque_capa_2 = Cabanas(self.parque_base, tipo="doble", capacidad=4)
        # Capa 3: Envolvemos el resultado con un Servicio Extra (Danza)
        parque_totalmente_decorado = ServicioParqueDecorator(
            servicio=parque_capa_2,
            servicio_extra="Show Nocturno",
            horario="20:00 - 22:00",
            capacidad=100
        )

        # El nombre debe haber acumulado las transformaciones de toda la cadena de envolturas
        nombre_esperado = "Parque Bicentenario (+ Cabañas doble)"
        self.assertEqual(parque_totalmente_decorado.getNombre(), nombre_esperado)
        
        # El horario final debe ser el de la última envoltura
        self.assertEqual(parque_totalmente_decorado.getHorario(), "20:00 - 22:00")
        self.assertIn("Servicio extra: Show Nocturno", str(parque_totalmente_decorado))