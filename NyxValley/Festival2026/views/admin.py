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


@login_required
def panel_admin(request):
    """Panel principal del administrador."""
    if not request.user.is_admin:
        return redirect('inicio')
    return render(request, 'admin/panel.html')


@login_required
def gestionar_reservaciones(request):
    """Lista todas las reservaciones para el administrador (RF-13, RF-14)."""
    if not request.user.is_admin:
        return redirect('inicio')
    reservaciones = Reservacion.objects.all().order_by('-fecha_creacion')
    return render(request, 'admin/gestionar_reservaciones.html',
                  {'reservaciones': reservaciones})


@login_required
def consultar_reservas(request):
    """Consulta de reservaciones con filtros (RF-13)."""
    if not request.user.is_admin:
        return redirect('inicio')
    # TODO: Alan — agregar filtros por parque, fecha y tipo de estancia
    reservaciones = Reservacion.objects.all()
    return render(request, 'admin/consultar_reservas.html',
                  {'reservaciones': reservaciones})


@login_required
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

    return render(request, 'admin/editar_parque.html', {
        'form': form,
        'parque': parque,
    })


@login_required
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