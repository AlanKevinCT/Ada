from django.test import TestCase
from datetime import time
from ..models import Parque
from ..mapa import MapaNavegacion

class TestMapaNavegacionBackend(TestCase):

    def setUp(self):
        """Configuración de parques con diferentes estados de activación y coordenadas."""
        self.mapa_servicio = MapaNavegacion()

        self.parque_activo = Parque.objects.create(
            nombre="Parque Bicentenario",
            direccion="CDMX, México",
            servicios="Camping, sanitarios",
            horario_apertura=time(8, 0),
            horario_cierre=time(17, 0),
            latitud=19.5855,
            longitud=-100.2831,
            activo=True
        )

        # 2. Parque activo pero sin coordenadas
        self.parque_sin_coordenadas = Parque.objects.create(
            nombre="Parque Incompleto",
            direccion="Toluca, México",
            horario_apertura=time(9, 0),
            horario_cierre=time(18, 0),
            latitud=None,
            longitud=None,
            activo=True
        )

        # 3. Parque con coordenadas pero inactivo
        self.parque_inactivo = Parque.objects.create(
            nombre="Parque Clausurado",
            direccion="Morelos, México",
            horario_apertura=time(8, 0),
            horario_cierre=time(17, 0),
            latitud=18.9220,
            longitud=-99.2340,
            activo=False
        )

    # ─────────────────────────────────────────────────────────────
    #  1. Creacion del mapa y consulta de parques
    # ─────────────────────────────────────────────────────────────
    def test_iniciar_mapa_muestra_parques_validos(self):
        """Verifica que el mapa solo recupere los parques que están activos y con coordenadas."""
        parques_cargados = self.mapa_servicio.iniciarMapa()
        
        # Debe recuperar exactamente 1 parque (el Bicentenario)
        self.assertEqual(len(parques_cargados), 1)
        self.assertEqual(parques_cargados[0]['nombre'], "Parque Bicentenario")
        
        # No debe incluir parque inválidoss (sin coordenadas o inactivos)
        ids_cargados = [p['id'] for p in parques_cargados]
        self.assertNotIn(self.parque_sin_coordenadas.id, ids_cargados)
        self.assertNotIn(self.parque_inactivo.id, ids_cargados)

    def test_ver_parque_especifico(self):
        """Verifica la consulta de un parque que existe y uno invalido."""
        # Parque activo existente
        info_parque = self.mapa_servicio.verParque(self.parque_activo.id)
        self.assertIsNotNone(info_parque)
        self.assertEqual(info_parque['nombre'], "Parque Bicentenario")
        self.assertEqual(info_parque['latitud'], 19.5855)
        self.assertEqual(info_parque['longitud'], -100.2831)
        self.assertEqual(info_parque['direccion'], "CDMX, México")

        #  Parque inactivo
        info_inactivo = self.mapa_servicio.verParque(self.parque_inactivo.id)
        self.assertIsNone(info_inactivo, "El mapa no debe mostrar los datos de parques inactivos.")

    # ─────────────────────────────────────────────────────────────
    #  2. Zoom
    # ─────────────────────────────────────────────────────────────
    def test_utilidad_zoom_retorna_parametros_correctos(self):
        """Verifica que la función auxiliar de zoom ensamble bien su diccionario."""
        config_zoom = self.mapa_servicio.zoom(19.5855, -100.2831, nivel=15)
        self.assertEqual(config_zoom['latitud'], 19.5855)
        self.assertEqual(config_zoom['longitud'], -100.2831)
        self.assertEqual(config_zoom['zoom'], 15)

    # ─────────────────────────────────────────────────────────────
    #  3. formateo de datos para GeoJSON
    # ─────────────────────────────────────────────────────────────
    def test_parques_como_geojson_cumple_especificacion_estandar(self):
        """Verifica que la estructura dict generada sea una FeatureCollection GeoJSON válida."""
        geojson = self.mapa_servicio.parques_como_geojson()
        
        # 1. Validamos la cabecera estándar de GeoJSON
        self.assertEqual(geojson['type'], 'FeatureCollection')
        self.assertIn('features', geojson)
        self.assertEqual(len(geojson['features']), 1)

        # 2. Validamos la anatomía del primer Feature (marcador)
        feature = geojson['features'][0]
        self.assertEqual(feature['type'], 'Feature')
        
        self.assertEqual(feature['geometry']['type'], 'Point')
        self.assertEqual(feature['geometry']['coordinates'], [-100.2831, 19.5855])

        # 3. Validamos el formateo de strings de los horarios (Línea crítica del strftime)
        properties = feature['properties']
        self.assertEqual(properties['nombre'], "Parque Bicentenario")
        self.assertEqual(properties['horario_apertura'], "08:00")
        self.assertEqual(properties['horario_cierre'], "17:00")