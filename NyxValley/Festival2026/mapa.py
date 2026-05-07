from .models import Parque


# ─────────────────────────────────────────────────────────────
#  MapaNavegacion  (del diagrama — conecta con «external» MapaAPI)
#  Lógica del mapa interactivo (RF-07, RF-08, RF-09)
#  Ayros se encarga de la implementación completa de esta clase
# ─────────────────────────────────────────────────────────────

class MapaNavegacion:

    def __init__(self):
        self._parques = []

    def iniciarMapa(self) -> list:
        """
        Carga todos los parques activos con coordenadas
        para mostrarlos en el mapa interactivo.
        """
        self._parques = list(
            Parque.objects.filter(
                activo=True,
                latitud__isnull=False,
                longitud__isnull=False,
            ).values(
                'id',
                'nombre',
                'direccion',
                'servicios',
                'horario',
                'latitud',
                'longitud',
                'tiene_cabanas',
                'tiene_camping',
            )
        )
        return self._parques

    def verParque(self, parque_id: int) -> dict | None:
        """
        Devuelve la información de un parque específico
        al hacer clic en su marcador (pin) en el mapa.
        """
        try:
            parque = Parque.objects.get(id=parque_id, activo=True)
            return {
                'id':            parque.id,
                'nombre':        parque.nombre,
                'direccion':     parque.direccion,
                'servicios':     parque.servicios,
                'horario':       parque.horario,
                'latitud':       float(parque.latitud),
                'longitud':      float(parque.longitud),
                'tiene_cabanas': parque.tiene_cabanas,
                'tiene_camping': parque.tiene_camping,
                'capacidad':     parque.capacidad,
            }
        except Parque.DoesNotExist:
            return None

    def zoom(self, latitud: float, longitud: float,
             nivel: int = 12) -> dict:
        """
        Devuelve los parámetros de zoom para centrar
        el mapa en una coordenada específica.
        """
        return {
            'latitud':  latitud,
            'longitud': longitud,
            'zoom':     nivel,
        }

    def parques_como_geojson(self) -> dict:
        """
        Convierte los parques a formato GeoJSON —
        compatible con Leaflet y Google Maps API.
        Útil cuando implementes el mapa en el frontend.
        """
        parques = self.iniciarMapa()
        features = []

        for p in parques:
            features.append({
                'type': 'Feature',
                'geometry': {
                    'type':        'Point',
                    'coordinates': [float(p['longitud']), float(p['latitud'])],
                },
                'properties': {
                    'id':            p['id'],
                    'nombre':        p['nombre'],
                    'direccion':     p['direccion'],
                    'servicios':     p['servicios'],
                    'horario':       p['horario'],
                    'tiene_cabanas': p['tiene_cabanas'],
                    'tiene_camping': p['tiene_camping'],
                },
            })

        return {
            'type':     'FeatureCollection',
            'features': features,
        }