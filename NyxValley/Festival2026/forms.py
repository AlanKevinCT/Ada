# forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import Usuario, Parque, Reservacion
from .services import Disponibilidad

class RegistroForm(forms.ModelForm):
    password           = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'})
    )
    confirmar_password = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Repite la contraseña'})
    )

    class Meta:
        model  = Usuario
        fields = [
            'correo_electronico',
            'nombre',
            'apellido_paterno',
            'apellido_materno',
        ]
        widgets = {
            'correo_electronico': forms.EmailInput(attrs={'placeholder': 'correo@ejemplo.com'}),
            'nombre':             forms.TextInput(attrs={'placeholder': 'Nombre'}),
            'apellido_paterno':   forms.TextInput(attrs={'placeholder': 'Apellido paterno'}),
            'apellido_materno':   forms.TextInput(attrs={'placeholder': 'Apellido materno'}),
        }

    def clean_correo_electronico(self):
        correo = self.cleaned_data['correo_electronico']
        if Usuario.objects.filter(correo_electronico=correo).exists():
            raise ValidationError('Este correo ya está registrado.')
        return correo

    def clean(self):
        cleaned_data = super().clean()
        password   = cleaned_data.get('password')
        confirmar  = cleaned_data.get('confirmar_password')
        if password and confirmar and password != confirmar:
            raise ValidationError('Las contraseñas no coinciden.')
        return cleaned_data

class LoginForm(forms.Form):
    correo_electronico = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={'placeholder': 'correo@ejemplo.com'})
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'})
    )

class ReservaForm(forms.Form):
    parque = forms.ModelChoiceField(
        queryset=Parque.objects.filter(activo=True),
        label='Parque',
        empty_label='— Selecciona un parque —',
    )
    fecha_inicio = forms.DateField(
        label='Fecha de inicio',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    fecha_fin = forms.DateField(
        label='Fecha de fin',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    numero_personas = forms.IntegerField(
        label='Número de personas',
        min_value=1,
    )
    tipo_visita = forms.ChoiceField(
        label='Tipo de visita',
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
                    'Las fechas no son válidas: deben estar entre junio y agosto '
                    'y no pueden incluir martes.'
                )

        if parque and tipo_visita == 'cabana' and not Parque.tiene_cabanas:
            raise ValidationError(
                f'El parque {parque.nombre} no cuenta con cabañas. '
                'Elige zona de camping u otro parque.'
            )

        if parque and fecha_inicio and fecha_fin and tipo_visita:
            if not Disponibilidad.verificarDisponible(
                parque, fecha_inicio, fecha_fin, tipo_visita
            ):
                raise ValidationError(
                    'No hay disponibilidad en el parque para esas fechas.'
                )

        return cleaned_data