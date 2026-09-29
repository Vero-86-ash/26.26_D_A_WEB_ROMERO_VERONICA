# forms/login_form.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email

class LoginForm(FlaskForm):
    email = StringField(
        'Correo Electrónico',
        validators=[
            DataRequired(message='El correo electrónico es obligatorio.'),
            Email(message='Ingrese un correo electrónico válido.')
        ],
        render_kw={
            'placeholder': 'ejemplo@correo.com',
            'class': 'form-control bg-dark text-white border-secondary',
            'autocomplete': 'email'
        }
    )

    password = PasswordField(
        'Contraseña',
        validators=[
            DataRequired(message='La contraseña es obligatoria.')
        ],
        render_kw={
            'placeholder': '••••••••',
            'class': 'form-control bg-dark text-white border-secondary',
            'autocomplete': 'current-password'
        }
    )

    captcha = StringField(
        'Código de Seguridad',
        validators=[
            DataRequired(message='Debe ingresar los caracteres de la imagen.')
        ],
        render_kw={
            'placeholder': 'Ingrese el texto de la imagen',
            'class': 'form-control bg-dark text-white border-secondary text-uppercase text-center fw-bold letter-spacing-2',
            'autocomplete': 'off'
        }
    )

    submit = SubmitField(
        'Ingresar al sistema',
        render_kw={'class': 'btn btn-warning fw-bold text-dark w-100 py-2'}
    )