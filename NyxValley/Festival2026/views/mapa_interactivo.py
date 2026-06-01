from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse

from ..models import Parque
from ..mapa import MapaNavegacion

import json

def mapa(request):
    """
    Muestra el mapa interactivo con los parques oficiales (RF-07, RF-08).
    Ayros implementa esta vista.
    """
    mapa_nav = MapaNavegacion()
    parques  = mapa_nav.iniciarMapa()
    geojson  = mapa_nav.parques_como_geojson()
    # json.dumps convierte True/False de Python a true/false de JavaScript
    geojson_str = json.dumps(geojson)
    return render(request, 'mapa/mapa.html', {
        'parques': parques,
        'geojson': geojson_str,
    })

def detalle_parque(request, id):
    """
    Devuelve la información de un parque al hacer clic en su pin (RF-09).
    Ayros implementa esta vista.
    """
    mapa_nav = MapaNavegacion()
    parque   = mapa_nav.verParque(id)
    if parque is None:
        return JsonResponse({'error': 'Parque no encontrado'}, status=404)
    # Si la petición es HTMX devuelve solo el fragmento HTML
    if request.headers.get('HX-Request'):
        return render(request, 'mapa/detalle_parque.html', {'parque': parque})
    return JsonResponse(parque)

def info_completa_parque(request, id):
    """
    Carga la página de aterrizaje (Landing Page) con toda la información 
    detallada, historia, galería y servicios de un parque específico.
    """
    parque = get_object_or_404(Parque, id=id)
    return render(request, 'mapa/info_completa.html', {'parque': parque})