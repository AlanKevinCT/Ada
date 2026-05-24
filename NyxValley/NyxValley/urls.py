from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from Festival2026 import views

urlpatterns = [

    # ─── Django admin (panel interno) ────────────────────────
    path('django-admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),

    # ─── Autenticación ───────────────────────────────────────
    path('',        views.inicio,    name='inicio'),
    path('registro/', views.registro, name='registro'),
    path('login/',    views.login,    name='login'),
    path('logout/',   views.logout,   name='logout'),

    # ─── Panel de cliente ────────────────────────────────────
    path('panel/',                          views.panel_cliente,      name='panel_cliente'),
    path('mis-reservaciones/',              views.mis_reservaciones,  name='mis_reservaciones'),
    path('mis-reservaciones/cancelar/<int:id>/', views.cancelar_reservacion, name='cancelar_reservacion'),

    # ─── Mapa interactivo ────────────────────────────
    path('mapa/',                   views.mapa,          name='mapa'),
    path('mapa/parque/<int:id>/',   views.detalle_parque, name='detalle_parque'),
    path('parque/<int:id>/detalle-completo/', views.info_completa_parque, name='info_completa_parque'),

    # ─── Reservaciones (cliente) ─────────────────────────────
    path('reservar/',                views.formulario_reserva, name='formulario_reserva'),
    path('reservar/confirmacion/',   views.confirmacion,       name='confirmacion'),

    # ─── Panel de administrador ──────────────────────────────
    path('admin-panel/',                            views.panel_admin,          name='panel_admin'),
    path('admin-panel/reservaciones/',              views.gestionar_reservaciones, name='gestionar_reservaciones'),
    path('admin-panel/reservaciones/consultar/',    views.consultar_reservas,   name='consultar_reservas'),
    path('admin-panel/parques/crear/',              views.crear_parque,         name='crear_parque'),
    path('admin-panel/parques/editar/<int:id>/',    views.editar_parque,        name='editar_parque'),
    path('admin-panel/parques/eliminar/<int:id>/',  views.eliminar_parque,      name='eliminar_parque'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)