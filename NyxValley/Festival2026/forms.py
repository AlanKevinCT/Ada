# forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import Usuario, Parque, Reservacion
from .services import Disponibilidad
from django.utils.translation import gettext_lazy as _
import re


# ─── Helpers de sanitización ──────────────────────────────────

def sanitizar_texto(valor):
    """
    Elimina caracteres peligrosos de campos de texto.
    Protege contra XSS e inyecciones.
    """
    if not valor:
        return valor
    # Eliminar tags HTML
    valor = re.sub(r'<[^>]+>', '', valor)
    # Eliminar caracteres de control
    valor = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', valor)
    return valor.strip()


def validar_solo_letras(valor, campo):
    """Valida que el campo solo contenga letras y espacios."""
    if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-]+$', valor):
        raise ValidationError(
            _(f'{campo} solo puede contener letras y espacios.')
        )
    return valor


def validar_contrasena_fuerte(password):
    """
    Valida que la contraseña sea fuerte:
    - Mínimo 8 caracteres
    - Al menos una mayúscula
    - Al menos una minúscula
    - Al menos un número
    - Al menos un carácter especial
    """
    if len(password) < 8:
        raise ValidationError(
            _('La contraseña debe tener al menos 8 caracteres.')
        )
    if not re.search(r'[A-Z]', password):
        raise ValidationError(
            _('La contraseña debe contener al menos una letra mayúscula.')
        )
    if not re.search(r'[a-z]', password):
        raise ValidationError(
            _('La contraseña debe contener al menos una letra minúscula.')
        )
    if not re.search(r'\d', password):
        raise ValidationError(
            _('La contraseña debe contener al menos un número.')
        )
    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-]', password):
        raise ValidationError(
            _('La contraseña debe contener al menos un carácter especial (!@#$%...).')
        )
    return password


# ─── Formulario de Registro ───────────────────────────────────

class RegistroForm(forms.ModelForm):
    password = forms.CharField(
        label=_('Contraseña'),
        widget=forms.PasswordInput(attrs={'placeholder': _('Contraseña')}),
        min_length=8,
    )
    confirmar_password = forms.CharField(
        label=_('Confirmar contraseña'),
        widget=forms.PasswordInput(attrs={'placeholder': _('Repite la contraseña')}),
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
            'correo_electronico': forms.EmailInput(
                attrs={'placeholder': 'correo@ejemplo.com', 'autocomplete': 'off'}
            ),
            'nombre':           forms.TextInput(attrs={'placeholder': _('Nombre')}),
            'apellido_paterno': forms.TextInput(attrs={'placeholder': _('Apellido paterno')}),
            'apellido_materno': forms.TextInput(attrs={'placeholder': _('Apellido materno')}),
        }

    def clean_correo_electronico(self):
        correo = self.cleaned_data['correo_electronico'].lower().strip()
        # Validar formato estricto de correo
        if not re.match(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$', correo):
            raise ValidationError(_('El formato del correo electrónico no es válido.'))
        # Mensaje genérico — no revelar si el correo existe (evita enumeración)
        if Usuario.objects.filter(correo_electronico=correo).exists():
            raise ValidationError(_('No fue posible completar el registro. Verifica tus datos.'))
        return correo

    def clean_nombre(self):
        nombre = sanitizar_texto(self.cleaned_data.get('nombre', ''))
        if len(nombre) < 2:
            raise ValidationError(_('El nombre debe tener al menos 2 caracteres.'))
        if len(nombre) > 100:
            raise ValidationError(_('El nombre no puede exceder 100 caracteres.'))
        return validar_solo_letras(nombre, 'Nombre')

    def clean_apellido_paterno(self):
        apellido = sanitizar_texto(self.cleaned_data.get('apellido_paterno', ''))
        if len(apellido) < 2:
            raise ValidationError(_('El apellido paterno debe tener al menos 2 caracteres.'))
        return validar_solo_letras(apellido, 'Apellido paterno')

    def clean_apellido_materno(self):
        apellido = sanitizar_texto(self.cleaned_data.get('apellido_materno', ''))
        if len(apellido) < 2:
            raise ValidationError(_('El apellido materno debe tener al menos 2 caracteres.'))
        return validar_solo_letras(apellido, 'Apellido materno')

    def clean_password(self):
        password = self.cleaned_data.get('password', '')
        return validar_contrasena_fuerte(password)

    def clean(self):
        cleaned_data = super().clean()
        password  = cleaned_data.get('password')
        confirmar = cleaned_data.get('confirmar_password')
        if password and confirmar and password != confirmar:
            raise ValidationError(_('Las contraseñas no coinciden.'))
        return cleaned_data


# ─── Formulario de Login ──────────────────────────────────────

class LoginForm(forms.Form):
    correo_electronico = forms.EmailField(
        label=_('Correo electrónico'),
        widget=forms.EmailInput(
            attrs={'placeholder': 'correo@ejemplo.com', 'autocomplete': 'off'}
        ),
        max_length=254,  # límite estándar RFC 5321
    )
    password = forms.CharField(
        label=_('Contraseña'),
        widget=forms.PasswordInput(attrs={'placeholder': _('Contraseña')}),
        max_length=128,  # evita ataques de contraseñas enormes (DoS)
    )

    def clean_correo_electronico(self):
        return self.cleaned_data['correo_electronico'].lower().strip()

    def clean_password(self):
        # Sanitizar sin revelar información
        password = self.cleaned_data.get('password', '')
        if len(password) > 128:
            raise ValidationError(_('Datos inválidos.'))
        return password


# ─── Formulario de Reserva ────────────────────────────────────

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
        max_value=500,  # límite razonable — evita valores absurdos
    )
    tipo_visita = forms.ChoiceField(
        label=_('Tipo de visita'),
        choices=Reservacion.TIPO_VISITA,
    )

    def clean_numero_personas(self):
        n = self.cleaned_data.get('numero_personas')
        if n is not None and (n < 1 or n > 500):
            raise ValidationError(_('El número de personas debe estar entre 1 y 500.'))
        return n

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin    = cleaned_data.get('fecha_fin')
        parque       = cleaned_data.get('parque')
        tipo_visita  = cleaned_data.get('tipo_visita')

        if fecha_inicio and fecha_fin:
            if fecha_inicio > fecha_fin:
                raise ValidationError(
                    _('La fecha de inicio no puede ser posterior a la fecha de fin.')
                )
            if not Disponibilidad.verificaFechas(fecha_inicio, fecha_fin):
                raise ValidationError(_('Las fechas no son válidas para el festival.'))

        if parque and tipo_visita == 'cabana' and not parque.tiene_cabanas:
            raise ValidationError(
                _('El parque {nombre} no cuenta con cabañas. Elige zona de camping u otro parque.').format(
                    nombre=parque.nombre
                )
            )

        if parque and fecha_inicio and fecha_fin and tipo_visita:
            if not Disponibilidad.verificarDisponible(
                parque, fecha_inicio, fecha_fin, tipo_visita
            ):
                raise ValidationError(
                    _('No hay disponibilidad en el parque para esas fechas.')
                )

        return cleaned_data