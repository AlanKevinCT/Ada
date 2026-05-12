# forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import Reservacion, Parque, Usuario
from .services import Disponibilidad

class RegistroForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirmar_password = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = Usuario
        fields = ['correo_electronico', 'nombre', 'apellido_paterno', 
                  'apellido_materno']
    
    def clean_correo_electronico(self):
        correo = self.cleaned_data['correo_electronico']
        if Usuario.objects.filter(correo_electronico=correo).exists():
            raise ValidationError('Este correo ya está registrado')
        return correo
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirmar = cleaned_data.get('confirmar_password')
        if password and confirmar and password != confirmar:
            raise ValidationError('Las contraseñas no coinciden')
        return cleaned_data
