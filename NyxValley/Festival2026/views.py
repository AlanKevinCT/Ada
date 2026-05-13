from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import Usuario, Parque, Reservacion
from .services import AsistReserva, Disponibilidad
from .mapa import MapaNavegacion


# ─────────────────────────────────────────────────────────────
#  Autenticación
# ─────────────────────────────────────────────────────────────

def inicio(request):
    """Página de inicio — accesible sin login."""
    return render(request, 'inicio.html')


def registro(request):
    """Registro de nuevo UsuarioCliente."""
    # TODO: Gera/Danna — implementar lógica de registro
    return render(request, 'registro.html')


def login(request):
    """Inicio de sesión para cliente y administrador."""
    # TODO: Gera/Danna — implementar lógica de login
    return render(request, 'login.html')


def logout(request):
    """Cierra la sesión activa."""
    auth_logout(request)
    return redirect('inicio')


# ─────────────────────────────────────────────────────────────
#  Panel de cliente
# ─────────────────────────────────────────────────────────────

@login_required
def panel_cliente(request):
    """Panel personal del usuario cliente."""
    # TODO: Gera/Danna — agregar contexto del usuario
    return render(request, 'cliente/panel.html')


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


# ─────────────────────────────────────────────────────────────
#  Mapa interactivo — Ayros
# ─────────────────────────────────────────────────────────────

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



# ─────────────────────────────────────────────────────────────
#  Reservaciones — cliente
# ─────────────────────────────────────────────────────────────

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


# ─────────────────────────────────────────────────────────────
#  Panel de administrador
# ─────────────────────────────────────────────────────────────

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
    # TODO: Gera/Danna — implementar formulario de creación
    return render(request, 'admin/crear_parque.html')


@login_required
def editar_parque(request, id):
    """Edita la información de un parque existente (RF-12)."""
    if not request.user.is_admin:
        return redirect('inicio')
    parque = get_object_or_404(Parque, id=id)
    # TODO: Gera/Danna — implementar formulario de edición
    return render(request, 'admin/editar_parque.html', {'parque': parque})


@login_required
def eliminar_parque(request, id):
    """Elimina un parque y notifica a los clientes afectados (RF-12)."""
    if not request.user.is_admin:
        return redirect('inicio')
    parque = get_object_or_404(Parque, id=id)
    if request.method == 'POST':
        from .signals import SignalModificacion
        SignalModificacion.borrarParque(parque)
        parque.delete()
        return redirect('panel_admin')
    return render(request, 'admin/eliminar_parque.html', {'parque': parque})