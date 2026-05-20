from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from ..models import Usuario, Parque, Reservacion
from ..services import AsistReserva, Disponibilidad
from ..mapa import MapaNavegacion
from ..forms import RegistroForm, LoginForm, ReservaForm
from ..signals import SignalCorreoCliente

from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import json

def inicio(request):
    """
    Página de inicio — accesible sin login. Muestra el mapa interactivo con los parques oficiales
    """
    mapa_nav = MapaNavegacion()
    parques  = mapa_nav.iniciarMapa()
    geojson  = mapa_nav.parques_como_geojson()
    geojson_str = json.dumps(geojson)
    return render(request, 'mapa/mapa.html', {
        'parques': parques,
        'geojson': geojson_str,
    })


# def enviar_bienvenida(usuario):
#     """Correo de bienvenida al registrarse (además del de reservación)."""
#     send_mail(
#         subject='¡Bienvenido al Festival Internacional de las Luciérnagas 2026!',
#         message=(
#             f'Hola {usuario.nombre},\n\n'
#             f'Tu cuenta ha sido creada exitosamente con el correo: '
#             f'{usuario.correo_electronico}\n\n'
#             f'Ya puedes explorar los parques y realizar tu reservación.\n\n'
#             f'¡Te esperamos en el festival!\n'
#         ),
#         from_email=settings.DEFAULT_FROM_EMAIL,
#         recipient_list=[usuario.correo_electronico],
#         fail_silently=True,
#     )

def registro(request):
     """Registro de nuevoUsuarioCliente."""
     form = RegistroForm()
     if request.method == 'POST':
        form = RegistroForm(data=request.POST)
        if form.is_valid():
            usuario = Usuario.objects.create_user(
                correo_electronico=form.cleaned_data['correo_electronico'],
                nombre=form.cleaned_data['nombre'],
                apellido_paterno=form.cleaned_data['apellido_paterno'],
                apellido_materno=form.cleaned_data['apellido_materno'],
                password=form.cleaned_data['password'],
            )
            SignalCorreoCliente.notifyRegistro(usuario)
            auth_login(request, usuario)
            return redirect('inicio')
     return render(request, 'registro.html', {'form': form})


def login(request):
    """Inicio de sesión para cliente y administrador (RF-02)."""
    form  = LoginForm()
    error = None

    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            correo   = form.cleaned_data['correo_electronico']
            password = form.cleaned_data['password']

            usuario = authenticate(
                request,
                username=correo, 
                password=password,
            )

            if usuario is not None:
                auth_login(request, usuario)
                # Redirige si el usuario es organizador
                if usuario.is_admin:
                    return redirect('panel_admin')
                return redirect('inicio')
            else:
                error = 'Correo o contraseña incorrectos.'

    return render(request, 'login.html', {'form': form, 'error': error})


def logout(request):
    """Cierra la sesión activa."""
    auth_logout(request)
    return redirect('inicio')

