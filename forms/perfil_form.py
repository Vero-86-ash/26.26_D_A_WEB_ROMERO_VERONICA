# forms/perfil_form.py
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp

class PerfilUsuarioForm(FlaskForm):
    """Formulario para actualizar datos personales del usuario logueado"""
    
    nombre = StringField(
        'Nombre',
        validators=[
            DataRequired(message='El nombre es obligatorio.'),
            Length(min=2, max=100, message='El nombre debe tener entre 2 y 100 caracteres.'),
            Regexp(
                r'^[A-ZÁÉÍÓÚÑ][a-záéíóúñA-ZÁÉÍÓÚÑ\s]*$',
                message='El nombre debe iniciar con mayúscula y contener únicamente letras.'
            )
        ],
        render_kw={
            'placeholder': 'Ej. Verónica',
            'class': 'form-control bg-dark text-white border-secondary'
        }
    )

    apellido = StringField(
        'Apellido',
        validators=[
            DataRequired(message='El apellido es obligatorio.'),
            Length(min=2, max=100, message='El apellido debe tener entre 2 y 100 caracteres.'),
            Regexp(
                r'^[A-ZÁÉÍÓÚÑ][a-záéíóúñA-ZÁÉÍÓÚÑ\s]*$',
                message='El apellido debe iniciar con mayúscula y contener únicamente letras.'
            )
        ],
        render_kw={
            'placeholder': 'Ej. Romero',
            'class': 'form-control bg-dark text-white border-secondary'
        }
    )

    telefono = StringField(
        'Número de Contacto / Celular',
        validators=[
            DataRequired(message='El número de teléfono es obligatorio.'),
            Regexp(
                r'^[0-9]{7,10}$',
                message='El teléfono debe contener únicamente números (entre 7 y 10 dígitos).'
            )
        ],
        render_kw={
            'placeholder': 'Ej. 0991234567',
            'class': 'form-control bg-dark text-white border-secondary',
            'maxlength': '10',
            'inputmode': 'numeric',
            'oninput': "this.value = this.value.replace(/[^0-9]/g, '')"
        }
    )

    submit = SubmitField(
        'Actualizar mis datos',
        render_kw={'class': 'btn btn-warning fw-bold text-dark w-100 py-2 shadow-sm'}
    )