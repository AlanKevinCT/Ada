# forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import Usuario, Parque, Reservacion, Servicio
from .services import Disponibilidad
from django.utils.translation import gettext_lazy as _

class RegistroForm(forms.ModelForm):
    password           = forms.CharField(
        label=_('Contraseña'),
        widget=forms.PasswordInput(attrs={'placeholder': _('Contraseña')})
    )
    confirmar_password = forms.CharField(
        label=_('Confirmar contraseña'),
        widget=forms.PasswordInput(attrs={'placeholder': _('Repite la contraseña')})
    )

    class Meta:
        model  = Usuario
        fields = [
            'correo_electronico',
            'nombre',
            'apellido_paterno',
            'apellido_materno',
        ]
        labels = {
            'correo_electronico': _('Correo electrónico'),
            'nombre':             _('Nombre'),
            'apellido_paterno':   _('Apellido paterno'),
            'apellido_materno':   _('Apellido materno'),
        }
        widgets = {
            'correo_electronico': forms.EmailInput(attrs={'placeholder': 'correo@ejemplo.com'}),
            'nombre':             forms.TextInput(attrs={'placeholder': _('Nombre')}),
            'apellido_paterno':   forms.TextInput(attrs={'placeholder': _('Apellido paterno')}),
            'apellido_materno':   forms.TextInput(attrs={'placeholder': _('Apellido materno')}),
        }

    def clean_correo_electronico(self):
        correo = self.cleaned_data['correo_electronico']
        if Usuario.objects.filter(correo_electronico=correo).exists():
            raise ValidationError(_('Este correo ya está registrado.'))
        return correo

    def clean(self):
        cleaned_data = super().clean()
        password   = cleaned_data.get('password')
        confirmar  = cleaned_data.get('confirmar_password')
        if password and confirmar and password != confirmar:
            raise ValidationError(_('Las contraseñas no coinciden.'))
        return cleaned_data

class LoginForm(forms.Form):
     correo_electronico = forms.EmailField(
        label=_('Correo electrónico'),
        widget=forms.EmailInput(attrs={'placeholder': 'correo@ejemplo.com'})
     )
     password = forms.CharField(
        label=_('Contraseña'),
        widget=forms.PasswordInput(attrs={'placeholder': _('Contraseña')})
        )

class ReservaForm(forms.Form):
    parque = forms.ModelChoiceField(
        queryset=Parque.objects.filter(activo=True),
        label=_('Parque'),
        empty_label=_('— Selecciona un parque —'),
    )
    fecha_inicio = forms.DateField(
        label=_('Fecha de inicio'),
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    fecha_fin = forms.DateField(
        label=_('Fecha de fin'),
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    numero_personas = forms.IntegerField(
        label=_('Número de personas'),
        min_value=1,
    )
    tipo_visita = forms.ChoiceField(
        label=_('Tipo de visita'),
        choices=Reservacion.TIPO_VISITA,
    )

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin    = cleaned_data.get('fecha_fin')
        parque       = cleaned_data.get('parque')
        tipo_visita  = cleaned_data.get('tipo_visita')

        if fecha_inicio and fecha_fin:
            if not Disponibilidad.verificaFechas(fecha_inicio, fecha_fin):
                raise ValidationError(
                    _('Las fechas no son válidas')
                )

        if parque and tipo_visita == 'cabana' and not parque.tiene_cabanas:
            raise ValidationError(
                _('El parque {nombre} no cuenta con cabañas. Elige zona de camping u otro parque.').format(nombre=parque.nombre)
            )

        if parque and fecha_inicio and fecha_fin and tipo_visita:
            if not Disponibilidad.verificarDisponible(
                parque, fecha_inicio, fecha_fin, tipo_visita
            ):
                raise ValidationError(
                    _('No hay disponibilidad en el parque para esas fechas.')
                )

        return cleaned_data

class ParqueForm(forms.ModelForm):
 
    class Meta:
        model  = Parque
        fields = [
            'nombre',
            'direccion',
            'horario_apertura',
            'horario_cierre',
            'latitud',
            'longitud',
            'capacidad',
            'activo',
            # Hospedaje
            'tiene_cabanas',
            'tiene_camping',
            'servicios',
        ]
        labels = {
            'nombre':           _('Nombre del parque'),
            'direccion':        _('Dirección'),
            'horario_apertura': _('Hora de apertura'),
            'horario_cierre':   _('Hora de cierre'),
            'latitud':          _('Latitud'),
            'longitud':         _('Longitud'),
            'capacidad':        _('Capacidad máxima (personas)'),
            'activo':           _('Visible en el mapa'),
            'tiene_cabanas':    _('Cabañas disponibles'),
            'tiene_camping':    _('Zona de camping'),
            'servicios':        _('Servicios'),
        }
        widgets = {
            'nombre':           forms.TextInput(attrs={'placeholder': _('Nombre del parque')}),
            'direccion':        forms.TextInput(attrs={'placeholder': _('Dirección completa')}),
            'horario_apertura': forms.TimeInput(attrs={'type': 'time'}),
            'horario_cierre':   forms.TimeInput(attrs={'type': 'time'}),
            'latitud':          forms.NumberInput(attrs={'placeholder': '19.432608', 'step': 'any'}),
            'longitud':         forms.NumberInput(attrs={'placeholder': '-99.133209', 'step': 'any'}),
            'capacidad':        forms.NumberInput(attrs={'min': 0}),
            'servicios':        forms.CheckboxSelectMultiple(),
        }
        help_texts = {
            'servicios':     _('Selecciona los servicios disponibles en este parque. '
                               'Puedes crear nuevos servicios desde la sección "Servicios".'),
            'tiene_camping': _('Todos los parques del festival deben incluir zona de camping.'),
        }
 
    def clean(self):
        cleaned_data     = super().clean()
        horario_apertura = cleaned_data.get('horario_apertura')
        horario_cierre   = cleaned_data.get('horario_cierre')
        tiene_camping    = cleaned_data.get('tiene_camping')
 
        if horario_apertura and horario_cierre:
            if horario_apertura >= horario_cierre:
                raise ValidationError({
                    'horario_apertura': _('La hora de apertura debe ser anterior a la de cierre.'),
                })
 
        if not tiene_camping:
            raise ValidationError({
                'tiene_camping': _('Todos los parques del festival deben incluir zona de camping.'),
            })
 
        return cleaned_data

class ServicioForm(forms.ModelForm):
 
    class Meta:
        model  = Servicio
        fields = ['nombre', 'descripcion']
        labels = {
            'nombre':      _('Nombre del servicio'),
            'descripcion': _('Descripción'),
        }
        widgets = {
            'nombre': forms.TextInput(attrs={
                'placeholder': _('Ej. Zona de fogatas, WiFi, Servicio médico…'),
            }),
            'descripcion': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': _('Descripción opcional del servicio.'),
            }),
        }
        help_texts = {
            'nombre': _('El nombre debe ser único. Se mostrará como etiqueta en el parque.'),
        }
 
    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        qs = Servicio.objects.filter(nombre__iexact=nombre)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError(
                _('Ya existe un servicio con el nombre "{nombre}".').format(nombre=nombre)
            )
        return nombre