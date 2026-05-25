from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from ..models import Usuario, Parque, Reservacion
from ..services import AsistReserva, Disponibilidad
from ..mapa import MapaNavegacion
from ..forms import ParqueForm
from ..signals import SignalModificacion

from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from datetime import datetime

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
     """
    Panel principal del administrador (RF-18).
    Controla las estadísticas del festival y el listado de santuarios autorizados.
    """
     if not request.user.is_admin:
        return redirect('inicio')
        
     parques_activos = Parque.objects.filter(activo=True)

     contexto = {
    'parques': parques_activos,
        'total_parques':        parques_activos.count(), 
        'total_reservaciones':  Reservacion.objects.count(),
        'reservaciones_activas':       Reservacion.objects.filter(estado='activa').count(), #
        'total_usuarios':       Usuario.objects.filter(is_admin=False).count(),
    }
     
     return render(request, 'admin/panel.html', contexto)

 

@login_required
@solo_admin
def consultar_reservas(request):
    """Consulta de reservaciones con filtros (RF-13)."""
    if not request.user.is_admin:
        return redirect('inicio')
    reservaciones = Reservacion.objects.all().order_by('-fecha_creacion') 
    parques = Parque.objects.all()

    parque_id = request.GET.get('parque')
    if parque_id:
        reservaciones = reservaciones.filter(parque_id=parque_id)

    fecha_filtro = request.GET.get('fecha')
    if fecha_filtro:
        reservaciones = reservaciones.filter(fecha_inicio=fecha_filtro)

    tipo_estancia = request.GET.get('tipo_estancia')
    if tipo_estancia in ['cabana', 'camping']:
        reservaciones = reservaciones.filter(tipo_visita=tipo_estancia)

    return render(request, 'admin/consultar_reservas.html', {
        'reservaciones': reservaciones,
        'parques': parques,
        'parque_seleccionado': parque_id,
        'fecha_seleccionada': fecha_filtro,
        'tipo_seleccionado': tipo_estancia,
    })


@login_required
@solo_admin
def crear_parque(request):
    """Crea un nuevo parque oficial (RF-12)."""
    if not request.user.is_admin:
        return redirect('inicio')

    form = ParqueForm()
    if request.method == 'POST':
        form = ParqueForm(data=request.POST)
        if form.is_valid():
            parque = form.save()
            SignalModificacion.agregarParque(parque)
            return redirect('panel_admin')

    return render(request, 'admin/crear_parque.html', {'form': form})


@login_required
@solo_admin
def editar_parque(request, id):
    """Edita la información de un parque existente (RF-12)."""
    if not request.user.is_admin:
        return redirect('inicio')
    parque = get_object_or_404(Parque, id=id)
    form   = ParqueForm(instance=parque)

    if request.method == 'POST':
        form = ParqueForm(data=request.POST, instance=parque)
        if form.is_valid():
            campos_modificados = []
            for campo in form.changed_data:
                label = form.fields[campo].label or campo
                campos_modificados.append(str(label))

            form.save()
            if campos_modificados:
                cambios = ', '.join(campos_modificados)
                SignalModificacion.modificarParque(parque, cambios)

            return redirect('panel_admin')
        else :
            print("ERRORES DEL FORMULARIO:", form.errors)

    return render(request, 'admin/editar_parque.html', {
        'form': form,
        'parque': parque,
    })


@login_required
@solo_admin
def eliminar_parque(request, id):
    """Elimina un parque y notifica a los clientes afectados (RF-12)."""
    if not request.user.is_admin:
        return redirect('inicio')
    parque = get_object_or_404(Parque, id=id)
    if request.method == 'POST':
        SignalModificacion.borrarParque(parque)
        parque.delete()
        return redirect('panel_admin')
    return render(request, 'admin/eliminar_parque.html', {'parque': parque})