from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from datetime import time
from django.core.exceptions import ValidationError

# ─────────────────────────────────────────────────────────────
#  Manager personalizado para nuestro Usuario
#  (necesario cuando usamos AbstractBaseUser)
# ─────────────────────────────────────────────────────────────
class UsuarioManager(BaseUserManager):

    def create_user(self, correo_electronico, nombre, apellido_paterno,
                    apellido_materno, password=None):
        if not correo_electronico:
            raise ValueError('El correo electrónico es obligatorio')
        usuario = self.model(
            correo_electronico=self.normalize_email(correo_electronico),
            nombre=nombre,
            apellido_paterno=apellido_paterno,
            apellido_materno=apellido_materno,
        )
        usuario.set_password(password)   # aplica hash SHA-256 (RNF-06)
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, correo_electronico, nombre, apellido_paterno,
                         apellido_materno, password=None):
        usuario = self.create_user(
            correo_electronico, nombre, apellido_paterno, apellido_materno, password
        )
        usuario.is_admin    = True
        usuario.is_staff    = True
        usuario.is_superuser = True
        usuario.save(using=self._db)
        return usuario


# ─────────────────────────────────────────────────────────────
#  Modelo base: Usuario  (RF-01, RF-02)
#  Reemplaza al User de Django para usar correo como login
# ─────────────────────────────────────────────────────────────
class Usuario(AbstractBaseUser, PermissionsMixin):

    correo_electronico = models.EmailField(unique=True)
    nombre             = models.CharField(max_length=100)
    apellido_paterno   = models.CharField(max_length=100)
    apellido_materno   = models.CharField(max_length=100)

    # Control de acceso
    is_active = models.BooleanField(default=True)
    is_staff  = models.BooleanField(default=False)   # puede entrar al admin de Django
    is_admin  = models.BooleanField(default=False)   # administrador del festival

    objects = UsuarioManager()

    # Django usará el correo en lugar del username para iniciar sesión
    USERNAME_FIELD  = 'correo_electronico'
    REQUIRED_FIELDS = ['nombre', 'apellido_paterno', 'apellido_materno']

    class Meta:
        verbose_name      = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f'{self.nombre} {self.apellido_paterno} <{self.correo_electronico}>'

    def nombre_completo(self):
        return f'{self.nombre} {self.apellido_paterno} {self.apellido_materno}'


# ─────────────────────────────────────────────────────────────
#  Parque  (RF-07, RF-08, RF-09, RF-12, RF-18)
# ─────────────────────────────────────────────────────────────
class Parque(models.Model):

    nombre    = models.CharField(max_length=200)
    direccion = models.CharField(max_length=300)
    servicios = models.TextField(help_text='Lista de servicios adicionales disponibles')


    # Para mostrar el horario en la vista de detalle del parque (RF-09)
    horario_apertura = models.TimeField(default=time(0, 0), help_text='Hora de apertura (HH:MM)')
    horario_cierre   = models.TimeField(default=time(0, 0), help_text='Hora de cierre (HH:MM)')

    # Todos tienen camping; solo algunos tienen cabañas (RF-18)
    tiene_danza = models.BooleanField(default=False)
    tiene_musica = models.BooleanField(default=False)
    tiene_teatro = models.BooleanField(default=False)
    tiene_transporte = models.BooleanField(default=False)
    tiene_banos = models.BooleanField(default=True)
    tiene_cafeterias = models.BooleanField(default=True)
    tiene_guias = models.BooleanField(default=False)

    # Hospedaje
    tiene_cabanas = models.BooleanField(default=False)
    tiene_camping = models.BooleanField(default=True)

    # Coordenadas para el mapa interactivo (RF-07)
    latitud  = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    capacidad = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)  # si False no aparece en el mapa

    class Meta:
        verbose_name      = 'Parque'
        verbose_name_plural = 'Parques'

    def __str__(self):
        return self.nombre
    
    def clean(self):
        if self.horario_apertura and self.horario_cierre:
            if self.horario_apertura >= self.horario_cierre:
                raise ValidationError({
                    'horario_apertura': 'La hora de apertura debe ser anterior a la de cierre.',
                })


# ─────────────────────────────────────────────────────────────
#  Reservacion  (RF-04, RF-05, RF-06, RF-10, RF-16, RF-17)
# ─────────────────────────────────────────────────────────────
class Reservacion(models.Model):

    TIPO_VISITA = [
        ('camping', 'Zona de Camping'),
        ('cabana',  'Cabaña'),
    ]

    ESTADO = [
        ('activa',    'Activa'),
        ('cancelada', 'Cancelada'),
    ]

    # Relaciones
    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name='reservaciones'
    )
    parque = models.ForeignKey(
        Parque, on_delete=models.CASCADE, related_name='reservaciones'
    )

    # Datos de la estancia (RF-10)
    fecha_inicio    = models.DateField()
    fecha_fin       = models.DateField()
    numero_personas = models.PositiveIntegerField()
    tipo_visita     = models.CharField(max_length=10, choices=TIPO_VISITA)

    # Estado de la reservación
    estado = models.CharField(max_length=10, choices=ESTADO, default='activa')

    # Fecha en que se creó el registro
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name      = 'Reservación'
        verbose_name_plural = 'Reservaciones'

    def __str__(self):
        return (f'Reservación de {self.usuario.nombre} '
                f'en {self.parque.nombre} '
                f'({self.fecha_inicio} → {self.fecha_fin})')

    def duracion_dias(self):
        return (self.fecha_fin - self.fecha_inicio).days