from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from ..models import Usuario, Parque, Reservacion
from ..services import AsistReserva, Disponibilidad
from ..mapa import MapaNavegacion

def mapa(request):
    """
    Muestra el mapa interactivo con los parques oficiales (RF-07, RF-08).
    Ayros implementa esta vista.
    """
    mapa_nav = MapaNavegacion()
    parques  = mapa_nav.iniciarMapa()
    geojson  = mapa_nav.parques_como_geojson()
    return render(request, 'mapa/mapa.html', {
        'parques': parques,
        'geojson': geojson,
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

