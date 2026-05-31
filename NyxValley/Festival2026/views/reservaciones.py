from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from ..models import Usuario, Parque, Reservacion
from ..services import AsistReserva, Disponibilidad
from ..mapa import MapaNavegacion
from ..forms import RegistroForm, LoginForm, ReservaForm

from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

@login_required
def formulario_reserva(request):
    """Formulario para realizar una reservación (RF-04, RF-10)."""
    parques = Parque.objects.filter(activo=True)
    form    = ReservaForm()
    if request.method == 'POST':
        form = ReservaForm(data=request.POST)
        if form.is_valid():
            try:
                reservacion = AsistReserva.reservar(
                    usuario=request.user,
                    parque=form.cleaned_data['parque'],
                    fecha_inicio=form.cleaned_data['fecha_inicio'],
                    fecha_fin=form.cleaned_data['fecha_fin'],
                    numero_personas=form.cleaned_data['numero_personas'],
                    tipo_visita=form.cleaned_data['tipo_visita'],
                )
                return render(request, 'cliente/formulario_reserva.html', {
                    'form': ReservaForm(), 
                    'parques': parques,
                    'success': True 
                })
                # ──────────────────────────────────────────────────────────────────
                
            except ValueError as e:
                form.add_error(None, str(e))
    else :
        initial_data = {}
        parque_id = request.GET.get('parque') # Captura el ?parque=3
        
        if parque_id:
            try:
                parque_seleccionado = parques.get(id=parque_id)
                initial_data['parque'] = parque_seleccionado
            except (Parque.DoesNotExist, ValueError):
                pass 
                
        form = ReservaForm(initial=initial_data)

    return render(request, 'cliente/formulario_reserva.html', {
        'form': form,
        'parques': parques,
    })

