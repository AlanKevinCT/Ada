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
                'horario_apertura',
                'horario_cierre',
                'latitud',
                'longitud',
                'tiene_cabanas',
                'tiene_camping',
                'tiene_danza',
                'tiene_musica',
                'tiene_teatro',
                'tiene_transporte',
                'tiene_banos',
                'tiene_cafeterias',
                'tiene_guias',
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
                'id':               parque.id,
                'nombre':           parque.nombre,
                'direccion':        parque.direccion,
                'servicios':        parque.servicios,
                'horario_apertura': parque.horario_apertura,
                'horario_cierre':   parque.horario_cierre,
                'latitud':          float(parque.latitud),
                'longitud':         float(parque.longitud),
                'tiene_danza':      parque.tiene_danza,
                'tiene_musica':     parque.tiene_musica,
                'tiene_teatro':     parque.tiene_teatro,
                'tiene_banos':      parque.tiene_baños,
                'tiene_cafeterias': parque.tiene_cafeterias,
                'tiene_guias':      parque.tiene_guias,
                'tiene_transporte': parque.tiene_transporte,
                'tiene_cabanas':    parque.tiene_cabanas,
                'tiene_camping':    parque.tiene_camping,
                'capacidad':        parque.capacidad,
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
                    'horario_apertura': p['horario_apertura'].strftime('%H:%M'),
                    'horario_cierre':   p['horario_cierre'].strftime('%H:%M'),
                    'tiene_danza':    p['tiene_danza'],
                    'tiene_musica':   p['tiene_musica'],
                    'tiene_teatro':   p['tiene_teatro'],
                    'tiene_banos':    p['tiene_banos'],
                    'tiene_cafeterias': p['tiene_cafeterias'],
                    'tiene_guias':    p['tiene_guias'],
                    'tiene_transporte': p['tiene_transporte'],
                    'tiene_cabanas': p['tiene_cabanas'],
                    'tiene_camping':  p['tiene_camping'],
                },
            })

        return {
            'type':     'FeatureCollection',
            'features': features,
        }