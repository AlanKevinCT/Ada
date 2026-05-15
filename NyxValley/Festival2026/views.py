from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import Usuario, Parque, Reservacion
from .services import AsistReserva, Disponibilidad
from .mapa import MapaNavegacion
from .forms import RegistroForm, LoginForm

from django.core.mail import send_mail
from django.conf import settings


# ─────────────────────────────────────────────────────────────
#  Autenticación
# ─────────────────────────────────────────────────────────────

def inicio(request):
    """Página de inicio — accesible sin login."""
    return render(request, 'inicio.html')

def enviar_bienvenida(usuario):
    """Correo de bienvenida al registrarse (además del de reservación)."""
    send_mail(
        subject='¡Bienvenido al Festival Internacional de las Luciérnagas 2026!',
        message=(
            f'Hola {usuario.nombre},\n\n'
            f'Tu cuenta ha sido creada exitosamente con el correo: '
            f'{usuario.correo_electronico}\n\n'
            f'Ya puedes explorar los parques y realizar tu reservación.\n\n'
            f'¡Te esperamos en el festival!\n'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[usuario.correo_electronico],
        fail_silently=True,
    )

def registro(request):
    """Registro de nuevo usuario cliente (RF-01)."""
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
            enviar_bienvenida(usuario)
            auth_login(request, usuario)
            return redirect('panel_cliente')

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
                return redirect('panel_cliente')
            else:
                error = 'Correo o contraseña incorrectos.'

    return render(request, 'login.html', {'form': form, 'error': error})


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

def mapa(request):
    """
    Muestra el mapa interactivo con los parques oficiales (RF-07, RF-08).
    Ayros implementa esta vista.
    """
    mapa_nav = MapaNavegacion()
    parques  = mapa_nav.iniciarMapa()
    geojson  = mapa_nav.parques_como_geojson()
    return render(request, 'mapa/mapa.html', {
        'parques': parques,
        'geojson': geojson,
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