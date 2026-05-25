from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from django.core import mail
from django.test import Client
from datetime import date, time
from ..models import Usuario, Parque, Reservacion

class TestSistemaFestivalEndToEnd(StaticLiveServerTestCase):

    def setUp(self):
        """Configuración del entorno real del sistema."""
        self.navegador = Client()
        
        self.password_valido = "DiegoValdez2026!"
        self.admin_password = "MarianaAdmin2026!"
        
        self.parque = Parque.objects.create(
            nombre='Parque Bicentenario', direccion='CDMX', servicios='Camping',
            horario_apertura=time(8,0), horario_cierre=time(17,0), capacidad=5,
            activo=True, tiene_camping=True, tiene_cabanas=True, latitud=19.4326, longitud=-99.1332
        )
        mail.outbox.clear()

    # ─────────────────────────────────────────────────────────────
    #  1. Flujo Completo de Ciclo de Vida del Cliente
    # ─────────────────────────────────────────────────────────────
    def test_ciclo_vida_cliente_autenticacion_y_sesion(self):
        """Verifica registro, login, inactividad y logout completo."""
        # A) Registro
        datos_registro = {
            'correo_electronico': 'pablo@ciencias.unam.mx', 'nombre': 'Pablo',
            'apellido_paterno': 'González', 'apellido_materno': 'Martínez',
            'password': self.password_valido, 'confirmar_password': self.password_valido
        }
        url_registro = self.live_server_url + reverse('registro')
        respuesta = self.navegador.post(url_registro, data=datos_registro, follow=True)
        self.assertEqual(respuesta.status_code, 200)
        
        # B) Validación de Correo: Registro Exitoso
        self.assertEqual(len(mail.outbox), 1)
        correo = mail.outbox[0]
        self.assertIn('pablo@ciencias.unam.mx', correo.to)
        self.assertEqual(correo.subject, '¡Bienvenido al Festival Internacional de las Luciérnagas 2026!')
        self.assertIn('Hola Pablo,', correo.body)
        self.assertIn('Tu cuenta ha sido creada exitosamente con el correo: pablo@ciencias.unam.mx', correo.body)

        # C) Cerrar sesión
        url_logout = self.live_server_url + reverse('logout')
        respuesta = self.navegador.get(url_logout, follow=True)
        self.assertFalse('_auth_user_id' in self.navegador.session)

        # D) Simular desconexión por inactividad
        self.navegador.login(correo_electronico='pablo@ciencias.unam.mx', password=self.password_valido)
        sesion = self.navegador.session
        sesion.set_expiry(0)
        sesion.save()

    # ─────────────────────────────────────────────────────────────
    #  2. Flujo de Mapa, Consulta de Evento/Parque y Reservación
    # ─────────────────────────────────────────────────────────────
    def test_navegacion_mapa_y_reservacion_exitosa(self):
        """Verifica navegación por el mapa interactivo, vista de detalles e inscripción exitosa."""
        Usuario.objects.create_user(
            correo_electronico='Veronica@ciencias.unam.mx', nombre='Veronica',
            apellido_paterno='Vargas', apellido_materno='López', password=self.password_valido
        )
        self.navegador.login(correo_electronico='Veronica@ciencias.unam.mx', password=self.password_valido)
        mail.outbox.clear()

        # A) Cargar Mapa
        url_mapa = self.live_server_url + reverse('mapa')
        respuesta_mapa = self.navegador.get(url_mapa)
        self.assertEqual(respuesta_mapa.status_code, 200)

        url_detalle = self.live_server_url + reverse('detalle_parque', kwargs={'id': self.parque.id})
        respuesta_htmx = self.navegador.get(url_detalle, HTTP_HX_Request='true')
        self.assertEqual(respuesta_htmx.status_code, 200)

        # B) Realizar reservación
        datos_reserva = {
            'parque': self.parque.id, 'fecha_inicio': date(2026, 6, 18),
            'fecha_fin': date(2026, 6, 20), 'numero_personas': 2, 'tipo_visita': 'camping'
        }
        url_reserva = self.live_server_url + reverse('formulario_reserva')
        respuesta_reserva = self.navegador.post(url_reserva, data=datos_reserva, follow=True)
        self.assertTemplateUsed(respuesta_reserva, 'cliente/confirmacion.html')
        
        # C) Validación de Correo: Reservación Confirmada
        self.assertEqual(len(mail.outbox), 1)
        correo_reserva = mail.outbox[0]
        self.assertIn('Veronica@ciencias.unam.mx', correo_reserva.to)
        self.assertEqual(correo_reserva.subject, '✨ Reservación confirmada — Festival de las Luciérnagas')
        self.assertIn('Hola Veronica,', correo_reserva.body)
        self.assertIn('Parque:          Parque Bicentenario', correo_reserva.body)
        self.assertIn('Fecha de inicio: 2026-06-18', correo_reserva.body)
        self.assertIn('Fecha de fin:    2026-06-20', correo_reserva.body)
        self.assertIn('Personas:        2', correo_reserva.body)

    # ─────────────────────────────────────────────────────────────
    #  3. Cancelación de Registros por el Cliente
    # ─────────────────────────────────────────────────────────────
    def test_cancelacion_de_reservas_desde_panel_cliente(self):
        """Verifica visualización de historial de registros y flujo de cancelación con aviso."""
        usuario = Usuario.objects.create_user(
            correo_electronico='marco@ciencias.unam.mx', nombre='Marco',
            apellido_paterno='Chávez', apellido_materno='García', password=self.password_valido
        )
        reserva = Reservacion.objects.create(
            usuario=usuario, parque=self.parque, fecha_inicio=date(2026,6,18),
            fecha_fin=date(2026,6,20), numero_personas=2, tipo_visita='camping'
        )
        self.navegador.login(correo_electronico='marco@ciencias.unam.mx', password=self.password_valido)
        mail.outbox.clear()

        # A) Ver lista
        url_mis_res = self.live_server_url + reverse('mis_reservaciones')
        respuesta_lista = self.navegador.get(url_mis_res)
        self.assertIn(reserva, respuesta_lista.context['reservaciones'])

        # B) Ejecutar proceso de cancelación
        url_cancelar = self.live_server_url + reverse('cancelar_reservacion', kwargs={'id': reserva.id})
        respuesta_cancelacion = self.navegador.post(url_cancelar, follow=True)
        self.assertEqual(respuesta_cancelacion.status_code, 200)

        # C) Validación de Correo: Cancelación Emitida por el Cliente
        self.assertEqual(len(mail.outbox), 1)
        correo_cancelacion = mail.outbox[0]
        self.assertIn('marco@ciencias.unam.mx', correo_cancelacion.to)
        self.assertEqual(correo_cancelacion.subject, 'Reservación cancelada — Festival de las Luciérnagas')
        self.assertIn('Hola Marco,', correo_cancelacion.body)
        self.assertIn('Tu reservación en Parque Bicentenario del 2026-06-18 al 2026-06-20 ha sido cancelada.', correo_cancelacion.body)
        self.assertIn('Si fue un error puedes volver a reservar desde tu cuenta.', correo_cancelacion.body)
        
        reserva.refresh_from_db()
        self.assertEqual(reserva.estado, 'cancelada')

    # ─────────────────────────────────────────────────────────────
    #  4. Operaciones CRUD del Administrador e Impacto Masivo
    # ─────────────────────────────────────────────────────────────
    def test_modulo_administrador_crud_parques_y_notificaciones(self):
        """Prueba de sistema para el CRUD de parques realizado por un administrador."""
        Usuario.objects.create_superuser(
            correo_electronico='admin@ciencias.unam.mx', nombre='Gerardo',
            apellido_paterno='Silva', apellido_materno='López', password=self.admin_password
        )
        cliente_afectado = Usuario.objects.create_user(
            correo_electronico='cliente_aviso@ciencias.unam.mx', nombre='Luis',
            apellido_paterno='Pérez', apellido_materno='Gómez', password=self.password_valido
        )
        self.navegador.login(correo_electronico='admin@ciencias.unam.mx', password=self.admin_password)
        mail.outbox.clear()

        # A) Crear Parque Oficial
        url_crear = self.live_server_url + reverse('crear_parque')
        datos_parque = {
            'nombre': 'Parque Tlalpan', 'direccion': 'Tlalpan CDMX', 'servicios': 'Camping',
            'horario_apertura': time(6,0), 'horario_cierre': time(16,0), 'capacidad': 100,
            'activo': True, 'tiene_camping': True, 'tiene_cabanas': False, 'latitud': 19.28, 'longitud': -99.19
        }
        self.navegador.post(url_crear, data=datos_parque)
        self.assertTrue(Parque.objects.filter(nombre='Parque Tlalpan').exists())

        # B) Editar Parque Oficial
        parque_creado = Parque.objects.get(nombre='Parque Tlalpan')
        
        # Le vinculamos una reservación activa a Luis en el nuevo parque para que sea destinatario del aviso
        Reservacion.objects.create(
            usuario=cliente_afectado, parque=parque_creado, fecha_inicio=date(2026,7,10),
            fecha_fin=date(2026,7,12), numero_personas=2, tipo_visita='camping', estado='activa'
        )
        mail.outbox.clear()

        url_editar = self.live_server_url + reverse('editar_parque', kwargs={'id': parque_creado.id})
        datos_parque['nombre'] = 'Parque Tlalpan MODIFICADO'
        self.navegador.post(url_editar, data=datos_parque)
        parque_creado.refresh_from_db()
        self.assertEqual(parque_creado.nombre, 'Parque Tlalpan MODIFICADO')

        # Validación de Correo: Modificación del Parque enviado a los usuarios con estancias activas
        self.assertEqual(len(mail.outbox), 1)
        correo_modificacion = mail.outbox[0]
        self.assertIn('cliente_aviso@ciencias.unam.mx', correo_modificacion.to)
        self.assertEqual(correo_modificacion.subject, 'Actualización de parque — Festival de las Luciérnagas')
        self.assertIn('Hola Luis,', correo_modificacion.body)
        self.assertIn('El parque Parque Tlalpan MODIFICADO ha sido actualizado:', correo_modificacion.body)
        mail.outbox.clear()

        # C) Eliminar Parque Oficial
        url_eliminar = self.live_server_url + reverse('eliminar_parque', kwargs={'id': parque_creado.id})
        self.navegador.post(url_eliminar)
        self.assertFalse(Parque.objects.filter(id=parque_creado.id).exists())

        # Validación de Correo: Notificación de eliminación masiva e impacto de cancelación de estancia
        self.assertEqual(len(mail.outbox), 1)
        correo_eliminacion = mail.outbox[0]
        self.assertIn('cliente_aviso@ciencias.unam.mx', correo_eliminacion.to)
        self.assertEqual(correo_eliminacion.subject, 'Actualización de parque — Festival de las Luciérnagas')
        self.assertIn('El parque Parque Tlalpan MODIFICADO ha sido eliminado del festival. Tu reservación ha sido cancelada automáticamente.', correo_eliminacion.body)

    # ─────────────────────────────────────────────────────────────
    #  5. Gestión de Usuarios y Auditoría por el Administrador
    # ─────────────────────────────────────────────────────────────

    def test_audita_reservaciones(self):
        """Verifica búsqueda filtrada de reservas y eliminación en cascada relacional."""
        Usuario.objects.create_superuser(
            correo_electronico='auditor@ciencias.unam.mx', nombre='Marco',
            apellido_paterno='Chávez', apellido_materno='Martínez', password=self.admin_password
        )
        cliente_problematico = Usuario.objects.create_user(
            correo_electronico='problematico@ciencias.unam.mx', nombre='Carlos',
            apellido_paterno='Gomez', apellido_materno='Calva', password=self.password_valido
        )
        reserva_auditable = Reservacion.objects.create(
            usuario=cliente_problematico, parque=self.parque, fecha_inicio=date(2026,6,18),
            fecha_fin=date(2026,6,20), numero_personas=4, tipo_visita='cabana'
        )
        self.navegador.login(correo_electronico='auditor@ciencias.unam.mx', password=self.admin_password)

        url_consultas = reverse('consultar_reservas')
        respuesta_filtros = self.navegador.get(url_consultas, {
            'parque': self.parque.id, 'tipo_visita': 'cabana', 'usuario': cliente_problematico.id
        })
        self.assertEqual(respuesta_filtros.status_code, 200)

        cliente_problematico.delete()
        self.assertFalse(Usuario.objects.filter(id=cliente_problematico.id).exists())
        self.assertFalse(Reservacion.objects.filter(id=reserva_auditable.id).exists())

    # ─────────────────────────────────────────────────────────────
    #  6. Tolerancia a Fallos, Control de Cupos Extremos y Permisos
    # ─────────────────────────────────────────────────────────────
    def test_manejo_errores_sistema_sobrecupo_credenciales_y_permisos(self):
        """Verifica control de errores ante hackeos de rutas, contraseñas mal metidas y sobrecupos."""
        url_login = reverse('login')
        respuesta_login = self.navegador.post(url_login, data={'correo_electronico': 'pablo@ciencias.unam.mx', 'password': 'falsa'})
        self.assertEqual(respuesta_login.status_code, 200)
        self.assertEqual(respuesta_login.context['error'], 'Correo o contraseña incorrectos.')

        Usuario.objects.create_user(
            correo_electronico='comun@ciencias.unam.mx', nombre='Usuario',
            apellido_paterno='Comun', apellido_materno='Comun', password=self.password_valido
        )
        self.navegador.login(correo_electronico='comun@ciencias.unam.mx', password=self.password_valido)
        url_panel_admin = reverse('panel_admin')
        respuesta_intruso = self.navegador.get(url_panel_admin, follow=True)
        self.assertTemplateUsed(respuesta_intruso, 'mapa/mapa.html')

        # Parque con capacidad 0 para simular sobrecupo
        self.parque.capacidad = 0
        self.parque.save()
        datos_sobrecupo = {
            'parque': self.parque.id, 'fecha_inicio': date(2026,6,18),
            'fecha_fin': date(2026,6,20), 'numero_personas': 2, 'tipo_visita': 'camping'
        }
        url_reserva = reverse('formulario_reserva')
        respuesta_cupo = self.navegador.post(url_reserva, data=datos_sobrecupo)
        
        self.assertEqual(respuesta_cupo.status_code, 200)
        self.assertTrue(len(respuesta_cupo.context['form'].non_field_errors()) > 0)