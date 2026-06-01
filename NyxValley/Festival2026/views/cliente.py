from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from ..models import Reservacion
from ..services import AsistReserva

@login_required
def panel_cliente(request):
    """Panel personal del usuario cliente."""
    return redirect('inicio')

@login_required
def mis_reservaciones(request):
    """Lista de reservaciones del usuario cliente (RF-06)."""
    reservaciones = Reservacion.objects.filter(
        usuario=request.user
    ).order_by('-fecha_creacion')
    return render(request, 'cliente/mis_reservaciones.html',
                  {'reservaciones': reservaciones})

@login_required
def cancelar_reservacion(request, id):
    """Cancela una reservación activa del cliente (RF-05)."""
    reservacion = get_object_or_404(Reservacion, id=id, usuario=request.user)
    if request.method == 'POST':
        AsistReserva.cancelarReserva(reservacion)
        return redirect('mis_reservaciones')
    return render(request, 'cliente/cancelar_reservacion.html',
                  {'reservacion': reservacion})