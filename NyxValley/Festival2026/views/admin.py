from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from ..models import Usuario, Parque, Reservacion
from ..services import AsistReserva, Disponibilidad
from ..mapa import MapaNavegacion
from ..forms import RegistroForm, LoginForm, ReservaForm
from ..signals import SignalModificacion

from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from functools import wraps
from django.shortcuts import redirect

def solo_admin(vista):
    """
    Decorador que reemplaza el patrón repetitivo
    if not request.user.is_admin: return redirect('inicio')
    Protege vistas de acceso no autorizado de manera limpia.
    """
    @wraps(vista)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin:
            return redirect('inicio')
        return vista(request, *args, **kwargs)
    return wrapper

@login_required
@solo_admin
def panel_admin(request):
    """Panel principal del administrador."""
    if not request.user.is_admin:
        return redirect('inicio')
    return render(request, 'admin/panel.html')


@login_required
@solo_admin
def gestionar_reservaciones(request):
    """Lista todas las reservaciones para el administrador (RF-13, RF-14)."""
    if not request.user.is_admin:
        return redirect('inicio')
    reservaciones = Reservacion.objects.all().order_by('-fecha_creacion')
    return render(request, 'admin/gestionar_reservaciones.html',
                  {'reservaciones': reservaciones})


@login_required
@solo_admin
def consultar_reservas(request):
    """Consulta de reservaciones con filtros (RF-13)."""
    if not request.user.is_admin:
        return redirect('inicio')
    # TODO: Alan — agregar filtros por parque, fecha y tipo de estancia
    reservaciones = Reservacion.objects.all()
    return render(request, 'admin/consultar_reservas.html',
                  {'reservaciones': reservaciones})


@login_required
@solo_admin
def crear_parque(request):
    """Crea un nuevo parque oficial (RF-12)."""
    if not request.user.is_admin:
        return redirect('inicio')
    # TODO: Gera/Danna — implementar formulario de creación
    return render(request, 'admin/crear_parque.html')


@login_required
@solo_admin
def editar_parque(request, id):
    """Edita la información de un parque existente (RF-12)."""
    if not request.user.is_admin:
        return redirect('inicio')
    parque = get_object_or_404(Parque, id=id)
    # TODO: Gera/Danna — implementar formulario de edición
    return render(request, 'admin/editar_parque.html', {'parque': parque})


@login_required
@solo_admin
def eliminar_parque(request, id):
    """Elimina un parque y notifica a los clientes afectados (RF-12)."""
    if not request.user.is_admin:
        return redirect('inicio')
    parque = get_object_or_404(Parque, id=id)
    if request.method == 'POST':
        #from signals import SignalModificacion
        SignalModificacion.borrarParque(parque)
        parque.delete()
        return redirect('panel_admin')
    return render(request, 'admin/eliminar_parque.html', {'parque': parque})