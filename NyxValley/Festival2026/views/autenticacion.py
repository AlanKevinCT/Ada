from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout

from ..models import Usuario
from ..mapa import MapaNavegacion
from ..forms import RegistroForm, LoginForm
from django.conf import settings
import json
from django.core.cache import cache # Importar para el rate limiting

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

            # 1. Definir una llave única para el usuario en la caché
            llave_cache = f"login_fallido_{correo}"
            intentos = cache.get(llave_cache, 0)

            # 2. Verificar si el usuario está bloqueado
            if intentos >= settings.LOGIN_MAX_INTENTOS:
                error = f"Demasiados intentos fallidos. Intenta de nuevo en 15 minutos."
                return render(request, 'login.html', {'form': form, 'error': error})

            usuario = authenticate(request, username=correo, password=password)

            if usuario is not None:
                auth_login(request, usuario)
                cache.delete(llave_cache) # 3. Limpiar intentos al entrar con éxito
                if usuario.is_admin:
                    return redirect('panel_admin')
                return redirect('inicio')
            else:
                # 4. Incrementar contador de fallos
                cache.set(llave_cache, intentos + 1, settings.LOGIN_BLOQUEO_SEGUNDOS)
                error = 'Correo o contraseña incorrectos.'

    return render(request, 'login.html', {'form': form, 'error': error})

def logout(request):
    """Cierra la sesión activa."""
    auth_logout(request)
    return redirect('inicio')