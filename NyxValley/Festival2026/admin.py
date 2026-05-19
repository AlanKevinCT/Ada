from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Parque, Reservacion


# ─── Admin de Usuario ─────────────────────────────────────────
@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display  = ('correo_electronico', 'nombre', 'apellido_paterno', 'is_admin', 'is_active')
    search_fields = ('correo_electronico', 'nombre', 'apellido_paterno')
    ordering      = ('correo_electronico',)

    fieldsets = (
        ('Credenciales',  {'fields': ('correo_electronico', 'password')}),
        ('Datos personales', {'fields': ('nombre', 'apellido_paterno', 'apellido_materno')}),
        ('Permisos',      {'fields': ('is_active', 'is_staff', 'is_admin', 'is_superuser')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('correo_electronico', 'nombre', 'apellido_paterno',
                       'apellido_materno', 'password1', 'password2'),
        }),
    )


# ─── Admin de Parque ──────────────────────────────────────────
@admin.register(Parque)
class ParqueAdmin(admin.ModelAdmin):
    list_display  = ('nombre', 'direccion', 'tiene_cabanas', 'tiene_camping', 'activo')
    search_fields = ('nombre', 'direccion')
    list_filter   = ('tiene_cabanas', 'activo')
    list_per_page = 10
    ordering      = ('nombre',)
    fieldsets = (
        ("Información general", {
            'fields': ('nombre', 'direccion', 'horario_apertura', 'horario_cierre','latitud', 'longitud'),   
        }),
        ('Servicios', {
            'fields': ('tiene_danza', 'tiene_musica',
                       'tiene_teatro', 'tiene_transporte',
                       'tiene_banos', 'tiene_cafeterias', 'tiene_guias'),
        }),
        ('Servicios adicionales', {
            'fields': ('servicios',),
        }),
        ('Hospedaje', {
            'fields': ('tiene_cabanas', 'tiene_camping'),
        }),
    )



# ─── Admin de Reservacion ─────────────────────────────────────
@admin.register(Reservacion)
class ReservacionAdmin(admin.ModelAdmin):
    list_display  = ('usuario', 'parque', 'fecha_inicio', 'fecha_fin',
                     'tipo_visita', 'estado', 'numero_personas')
    search_fields = ('usuario__correo_electronico', 'usuario__nombre', 'parque__nombre')
    list_filter   = ('estado', 'tipo_visita', 'parque')