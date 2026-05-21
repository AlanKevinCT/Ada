# forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import Usuario, Parque, Reservacion
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
            # Servicios (creo que vamos a tener que modificar esto :()
            'tiene_danza',
            'tiene_musica',
            'tiene_teatro',
            'tiene_transporte',
            'tiene_banos',
            'tiene_cafeterias',
            'tiene_guias',
            'tiene_cabanas',
            'tiene_camping',
            # Servicios (texto)
            'servicios',
        ]
        labels = {
            'nombre':            _('Nombre del parque'),
            'direccion':         _('Dirección'),
            'horario_apertura':  _('Hora de apertura'),
            'horario_cierre':    _('Hora de cierre'),
            'latitud':           _('Latitud'),
            'longitud':          _('Longitud'),
            'capacidad':         _('Capacidad máxima de personas'),
            'activo':            _('Visible en el mapa'),
            'tiene_danza':       _('Danza'),
            'tiene_musica':      _('Música'),
            'tiene_teatro':      _('Teatro'),
            'tiene_transporte':  _('Transporte'),
            'tiene_banos':       _('Baños'),
            'tiene_cafeterias':  _('Cafeterías'),
            'tiene_guias':       _('Guías'),
            'tiene_cabanas':     _('Cabañas'),
            'tiene_camping':     _('Zona de camping'),
            'servicios':         _('Otros servicios'),
        }
        widgets = {
            'nombre':           forms.TextInput(attrs={'placeholder': _('Nombre del parque')}),
            'direccion':        forms.TextInput(attrs={'placeholder': _('Dirección completa')}),
            'horario_apertura': forms.TimeInput(attrs={'type': 'time'}),
            'horario_cierre':   forms.TimeInput(attrs={'type': 'time'}),
            'latitud':          forms.NumberInput(attrs={'placeholder': '19.432608', 'step': 'any'}),
            'longitud':         forms.NumberInput(attrs={'placeholder': '-99.133209', 'step': 'any'}),
            'capacidad':        forms.NumberInput(attrs={'min': 0}),
            'servicios':        forms.Textarea(attrs={
                'rows': 3,
                'placeholder': _('Describe servicios adicionales disponibles en el parque'),
            }),
        }
 
    def clean(self):
        cleaned_data     = super().clean()
        horario_apertura = cleaned_data.get('horario_apertura')
        horario_cierre   = cleaned_data.get('horario_cierre')
 
        if horario_apertura and horario_cierre:
            if horario_apertura >= horario_cierre:
                raise ValidationError({
                    'horario_apertura': _('La hora de apertura debe ser anterior a la de cierre'),
                })
 
        tiene_cabanas = cleaned_data.get('tiene_cabanas')
        tiene_camping = cleaned_data.get('tiene_camping')
        if not tiene_cabanas and not tiene_camping:
            raise ValidationError(
                _('El parque debe ofrecer al menos zona de camping')
            )
 
        return cleaned_data
 