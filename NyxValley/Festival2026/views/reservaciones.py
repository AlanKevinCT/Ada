from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from ..models import Parque
from ..services import AsistReserva
from ..forms import  ReservaForm

@login_required
def formulario_reserva(request):
    """Formulario para realizar una reservación (RF-04, RF-10)."""
    parques = Parque.objects.filter(activo=True)
    form    = ReservaForm()
    if request.method == 'POST':
        form = ReservaForm(data=request.POST)
        if form.is_valid():
            try:
                AsistReserva.reservar(
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