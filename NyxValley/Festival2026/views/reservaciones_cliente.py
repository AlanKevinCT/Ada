from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from ..models import Usuario, Parque, Reservacion
from ..services import AsistReserva, Disponibilidad
from ..mapa import MapaNavegacion

@login_required
def formulario_reserva(request):
    """Formulario para realizar una reservación (RF-04, RF-10)."""
    # TODO: Gera/Danna — implementar formulario y validaciones
    parques = Parque.objects.filter(activo=True)
    return render(request, 'cliente/formulario_reserva.html',
                  {'parques': parques})


@login_required
def confirmacion(request):
    """Página de confirmación tras realizar una reservación (RF-11)."""
    # TODO: Gera/Danna — mostrar datos de la reservación recién creada
    return render(request, 'cliente/confirmacion.html')
