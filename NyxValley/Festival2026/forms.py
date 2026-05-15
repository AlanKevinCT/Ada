# forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import Usuario

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
    """
    Como nuestro modelo usa correo_electronico como USERNAME_FIELD,
    pero authenticate() de Django sigue esperando 'username'mapeamos aquí.
    """
    correo_electronico = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={'placeholder': 'correo@ejemplo.com'})
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'})
    )