from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from ..models import Usuario, Parque, Reservacion
from ..services import AsistReserva, Disponibilidad
from ..mapa import MapaNavegacion


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
