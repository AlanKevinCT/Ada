from django.test import TestCase
from ..models import Usuario, Parque, Reservacion
from datetime import date
from ..services import AsistReserva, Autenticador, Disponibilidad

class TestServiciosFestival(TestCase):

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

        self.reserva_base = Reservacion.objects.create(
            usuario=self.usuario,
            parque=self.parque,
            fecha_inicio=date(2026, 6, 10),
            fecha_fin=date(2026, 6, 12),
            numero_personas=2,
            tipo_visita='cabana',
            estado='activa'
        )


    # ─────────────────────────────────────────────────────────────
    #  Pruebas para el autenticador
    # ─────────────────────────────────────────────────────────────
    def test_generacion_contraseña(self):
        """Verifica que el autenticador genere una contraseña segura."""
        contraseña = "admin123"
        contraseña_hash = Autenticador.contrasenaHash(contraseña)
        self.assertNotEqual(contraseña, contraseña_hash)

    # ─────────────────────────────────────────────────────────────
    #  Pruebas para la disponibilidad
    # ─────────────────────────────────────────────────────────────
    def test_verificar_disponibilidad(self):
        """Verifica que el parque tenga disponibilidad para las fechas dadas."""
        fecha_inicio = date(2026, 6, 10)
        fecha_fin = date(2026, 6, 12)
        tipo_visita = 'cabana'
        disponible = Disponibilidad.verificarDisponible(
            self.parque, fecha_inicio, fecha_fin, tipo_visita
        )
        self.assertTrue(disponible)

    def test_verificar_fechas_validas(self):
        """Verifica que las fechas sean válidas para el festival."""
        fecha_inicio = date(2026, 7, 10) # inicio > fin
        fecha_fin = date(2026, 6, 12)
        fechas_validas = Disponibilidad.verificaFechas(fecha_inicio, fecha_fin)
        self.assertFalse(fechas_validas)

        # dias martes:
        fecha_inicio = date(2026, 6, 9)  # martes
        fecha_fin = date(2026, 6, 11)
        fechas_validas = Disponibilidad.verificaFechas(fecha_inicio, fecha_fin)
        self.assertFalse(fechas_validas)

        # meses validos:
        fecha_inicio = date(2026, 5, 10)  # mayo
        fecha_fin = date(2026, 5, 12)
        fechas_validas = Disponibilidad.verificaFechas(fecha_inicio, fecha_fin)
        self.assertFalse(fechas_validas)

    def test_bloqueo_martes_intermedio(self):
        """Debe rechazar rangos que contengan un martes en medio."""
        # Lunes 15 de Junio a Jueves 18 de Junio. El Martes 16 queda en medio.
        fecha_inicio = date(2026, 6, 15)
        fecha_fin = date(2026, 6, 18)
        
        with self.assertRaises(ValueError):
            AsistReserva.reservar(
                self.usuario, self.parque, fecha_inicio, fecha_fin, 2, 'cabana'
            )

    def test_verificar_hora_valida(self):
        """Verifica que la hora esté estrictamente dentro del horario del parque."""
        # 1. Hora dentro del rango (08:00 - 17:00)
        hora_valida = Disponibilidad.verificaHora('10:00')
        self.assertTrue(hora_valida, "Debería aceptar una hora dentro del rango del parque (10:00).")

        # 2. Hora fuera del rango (en la noche)
        hora_tarde = Disponibilidad.verificaHora('22:00')
        self.assertFalse(hora_tarde, "Debería rechazar una hora fuera del horario del parque (22:00).")

        # 3. Entrada inválida o nula
        hora_invalida = Disponibilidad.verificaHora(None)
        self.assertFalse(hora_invalida, "Debería rechazar un valor nulo (None) en la hora.")

    # ─────────────────────────────────────────────────────────────
    #  Pruebas para la lógica de reservaciones
    # ─────────────────────────────────────────────────────────────
    def test_reservacion_existosa(self):
        """Verifica que se pueda crear una reservación con datos válidos."""
        fecha_inicio = date(2026, 6, 10)
        fecha_fin = date(2026, 6, 12)
        numero_personas = 4
        tipo_visita = 'cabana'

        reservacion = AsistReserva.reservar(
            self.usuario, self.parque, fecha_inicio, fecha_fin,
            numero_personas, tipo_visita
        )

        self.assertIsNotNone(reservacion)
        self.assertEqual(reservacion.usuario, self.usuario)
        self.assertEqual(reservacion.parque, self.parque)
        self.assertEqual(reservacion.fecha_inicio, fecha_inicio)
        self.assertEqual(reservacion.fecha_fin, fecha_fin)
        self.assertEqual(reservacion.numero_personas, numero_personas)
        self.assertEqual(reservacion.tipo_visita, tipo_visita)

    def test_reservacion_sin_disponibilidad(self):
        """Verifica que no permita reservar si el parque está lleno."""
        # Bajamos la capacidad para forzar el error
        self.parque.capacidad = 1
        self.parque.save()
        
        # Ya existe una reserva en el setUp para el 10-12 de junio
        with self.assertRaises(ValueError) as cm:
            AsistReserva.reservar(
                self.usuario, self.parque, date(2026, 6, 10), date(2026, 6, 12), 1, 'cabana'
            )
        self.assertEqual(str(cm.exception), 'No hay disponibilidad en el parque para esas fechas.')

    def test_reserva_numero_personas_invalido(self):
        """Verifica que el sistema rechace reservaciones para 0 o menos personas."""
        # Intentar reservar para 0 personas deberia lanzar un error de negocio
        with self.assertRaises(ValueError):
            AsistReserva.reservar(
                self.usuario, self.parque, date(2026, 7, 15), date(2026, 7, 17), 0, 'camping'
            )

    def test_usuario_no_duplica_estancia(self):
        """Verifica que un usuario no pueda hacer dos reservas que se solapen en el tiempo."""
        # Ya tiene 'reserva_base' del 10 al 12 de junio.
        # Intentamos crear otra el 11 de junio (mientras está allá).
        with self.assertRaises(ValueError):
            AsistReserva.reservar(
                self.usuario, self.parque, date(2026, 6, 11), date(2026, 6, 13), 2, 'cabana'
            )

    def test_modificar_reserva(self):
        """Verifica que se puedan modificar las fechas de una reservación activa."""
        nueva_fecha_inicio = date(2026, 6, 24)
        nueva_fecha_fin = date(2026, 6, 26)

        resultado_modificacion = AsistReserva.modificarReserva(
            self.reserva_base, nueva_fecha_inicio, nueva_fecha_fin
        )
        self.assertTrue(resultado_modificacion)
        self.reserva_base.refresh_from_db()
        self.assertEqual(self.reserva_base.fecha_inicio, nueva_fecha_inicio)
        self.assertEqual(self.reserva_base.fecha_fin, nueva_fecha_fin)

    def test_modificar_reserva_fechas_invalidas(self):
        """Verifica que no se puedan modificar las fechas a valores inválidos."""
        # Dia fuera de rango (mayo) y martes incluido
        fecha_inicio_invalida = date(2026, 5, 10)
        fecha_fin_invalida = date(2026, 5, 12)
        with self.assertRaises(ValueError):
            AsistReserva.modificarReserva(
                self.reserva_base, fecha_inicio_invalida, fecha_fin_invalida
            )

        # Fechas invertidas (inicio después de fin)
        fecha_inicio_al_reves = date(2026, 7, 20)
        fecha_fin_al_reves = date(2026, 7, 15)
        
        with self.assertRaises(ValueError):
            AsistReserva.modificarReserva(
                self.reserva_base, fecha_inicio_al_reves, fecha_fin_al_reves
            )

        # Fechas pasadas (antes del 2026)
        fecha_pasado_inicio = date(2024, 7, 10) # Julio de 2024
        fecha_pasado_fin = date(2024, 7, 12)
        
        with self.assertRaises(ValueError):
            AsistReserva.reservar(
                self.usuario, self.parque, fecha_pasado_inicio, fecha_pasado_fin, 2, 'cabana'
            )

    def test_modificar_reserva_sin_disponibilidad(self):
        """Verifica que no se permita modificar fechas si el parque ya está lleno en el nuevo rango."""
        # Creamos una segunda reservación en un rango futuro (ej. 24 al 26 de junio)
        Reservacion.objects.create(
            usuario=self.usuario, parque=self.parque,
            fecha_inicio=date(2026, 6, 24), fecha_fin=date(2026, 6, 26),
            numero_personas=50, tipo_visita='cabana', estado='activa'
        )
        
        # Forzamos que la capacidad del parque sea 50 (ya está lleno para esas fechas del 24 al 26)
        self.parque.capacidad = 50
        self.parque.save()

        # Intentamos mover nuestra 'reserva_base' (que era del 10 al 12) hacia las fechas llenas.
        with self.assertRaises(ValueError):
            AsistReserva.modificarReserva(
                self.reserva_base, date(2026, 6, 24), date(2026, 6, 26)
            )

    def test_cancelar_reserva(self):
        """Verifica que se pueda cancelar una reservación activa."""
        resultado_cancelacion = AsistReserva.cancelarReserva(self.reserva_base)
        self.assertTrue(resultado_cancelacion)
        self.reserva_base.refresh_from_db()
        self.assertEqual(self.reserva_base.estado, 'cancelada')

    def test_cancelar_reserva_cancelada(self):
        """Verifica que no se pueda cancelar una reservación que no está activa."""
        AsistReserva.cancelarReserva(self.reserva_base)
        resultado_segunda_vez = AsistReserva.cancelarReserva(self.reserva_base)
        self.assertFalse(resultado_segunda_vez)

    def test_modificar_reserva_ya_cancelada(self):
        """Verifica que no se permita modificar las fechas de una reserva cancelada."""
        # Cancelamos la reserva primero
        AsistReserva.cancelarReserva(self.reserva_base)
        
        # Intentamos modificarla. Debería arrojar un error o denegar la operación.
        resultado = AsistReserva.modificarReserva(
            self.reserva_base, date(2026, 6, 17), date(2026, 6, 19)
        )
        self.assertFalse(resultado)