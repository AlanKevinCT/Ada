from django.test import TestCase, Client
from django.urls import reverse
from datetime import time
import json
from ...models import Parque

class TestMapaInteractivoReal(TestCase):

    def setUp(self):
        """Configuración del cliente HTTP y parques de prueba oficiales y ocultos."""
        self.client = Client()

        self.parque_activo = Parque.objects.create(
            nombre='Santuario El Rosario',
            direccion='Michoacán, México',
            servicios='Guías, Camping',
            horario_apertura=time(9, 0),
            horario_cierre=time(18, 0),
            capacidad=100,
            activo=True,
            latitud=19.5855,
            longitud=-100.2831
        )

        self.parque_oculto = Parque.objects.create(
            nombre='Parque en Mantenimiento',
            direccion='Zitácuaro, México',
            servicios='Ninguno',
            horario_apertura=time(8, 0),
            horario_cierre=time(16, 0),
            capacidad=50,
            activo=False,
            latitud=19.4326,
            longitud=-99.1332
        )

        # Mapeo de URLs
        self.url_mapa = reverse('mapa')
        self.url_detalle_activo = reverse('detalle_parque', kwargs={'id': self.parque_activo.id})
        self.url_info_activa = reverse('info_completa_parque', kwargs={'id': self.parque_activo.id})

    # ─────────────────────────────────────────────────────────────
    #  1. Vista General del Mapa
    # ─────────────────────────────────────────────────────────────
    def test_renderizacion_correcta_del_mapa_interactivo(self):
        """Verifica que el mapa interactivo se renderice correctamente en la vista del festival."""
        respuesta = self.client.get(self.url_mapa)
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, 'mapa/mapa.html')
    
        self.assertIn('parques', respuesta.context)
        self.assertIn('geojson', respuesta.context)

    def test_mapa_no_renderiza_parques_inactivos(self):
        """Verifica que no se rendericen parques no oficiales (inactivos) en el mapa interactivo."""
        respuesta = self.client.get(self.url_mapa)
        geojson_string = respuesta.context['geojson']
        
        self.assertIn('Santuario El Rosario', geojson_string)
        self.assertNotIn('Parque en Mantenimiento', geojson_string)

    # ─────────────────────────────────────────────────────────────
    #  2. Detalle del parque
    # ─────────────────────────────────────────────────────────────
    def test_detalle_parque(self):
        """Verifica que se devuelva la información correcta de un parque."""
        respuesta = self.client.get(self.url_detalle_activo)
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta['Content-Type'], 'application/json')
        
        datos = json.loads(respuesta.content.decode('utf-8'))
        self.assertEqual(datos['nombre'], 'Santuario El Rosario')   
        self.assertEqual(datos['direccion'], 'Michoacán, México')
        self.assertEqual(datos['servicios'], 'Guías, Camping') 
        self.assertEqual(datos['horario_apertura'], '09:00:00')
        self.assertEqual(datos['horario_cierre'], '18:00:00')
        self.assertEqual(datos['capacidad'], 100)

    def test_detalle_parque_devuelve_html(self):
        """Verifica que si la petición viene de HTMX, devuelva el fragmento HTML."""
        cabeceras_htmx = {'HTTP_HX_Request': 'true'}
        
        respuesta = self.client.get(self.url_detalle_activo, **cabeceras_htmx)
        
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, 'mapa/detalle_parque.html')

        parque_en_contexto = respuesta.context['parque']
        self.assertEqual(parque_en_contexto['nombre'], self.parque_activo.nombre)

    def test_detalle_parque_no_encontrado(self):
        """Verifica que el mapa devuelva un error si el parque consultado no existe."""
        url_invalida = reverse('detalle_parque', kwargs={'id': 99999})
        respuesta = self.client.get(url_invalida)
        
        self.assertEqual(respuesta.status_code, 404)
        datos = json.loads(respuesta.content.decode('utf-8'))
        self.assertEqual(datos['error'], 'Parque no encontrado')

    # ─────────────────────────────────────────────────────────────
    #  3. Pagina de información completa del parque
    # ─────────────────────────────────────────────────────────────
    def test_pagina_info_completa(self):
        """Verifica que la página de aterrizaje cargue con la información detallada."""
        respuesta = self.client.get(self.url_info_activa)
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, 'mapa/info_completa.html')
        self.assertEqual(respuesta.context['parque'], self.parque_activo)

    def test_pagina_info_completa_error_parque_no_existe(self):
        """Verifica que la página de información completa arroje un error si el parque no existe."""
        url_invalida = reverse('info_completa_parque', kwargs={'id': 99999})
        respuesta = self.client.get(url_invalida)
        
        self.assertEqual(respuesta.status_code, 404)