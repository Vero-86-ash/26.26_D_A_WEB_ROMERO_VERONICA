# forms/usuario_form.py
from flask_wtf import FlaskForm
from wtforms import PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp


class UsuarioRegistroForm(FlaskForm):
  cedula = StringField(
      'Cédula de Identidad',
      validators=[
          DataRequired(message='El número de cédula es obligatorio.'),
          Length(
              min=10,
              max=10,
              message='La cédula debe tener exactamente 10 dígitos.',
          ),
          Regexp(
              r'^[0-9]{10}$', message='La cédula solo debe contener números.'
          ),
      ],
      render_kw={
          'placeholder': 'Ej. 1723456789',
          'class': 'form-control bg-dark text-white border-secondary',
          'maxlength': '10',
          'pattern': '[0-9]*',
          'inputmode': 'numeric',
          'oninput': "this.value = this.value.replace(/[^0-9]/g, '')",
      },
  )

  nombre = StringField(
      'Nombres',
      validators=[
          DataRequired(message='El nombre es obligatorio.'),
          Length(
              min=2,
              max=80,
              message='El nombre debe tener entre 2 y 80 caracteres.',
          ),
          Regexp(
              r'^[A-ZÁÉÍÓÚÑ][a-záéíóúñA-ZÁÉÍÓÚÑ\s]*$',
              message=(
                  'El nombre debe iniciar con mayúscula y contener únicamente'
                  ' letras.'
              ),
          ),
      ],
      render_kw={
          'placeholder': 'Ej. Juan Carlos',
          'class': 'form-control bg-dark text-white border-secondary',
      },
  )

  apellido = StringField(
      'Apellidos',
      validators=[
          DataRequired(message='El apellido es obligatorio.'),
          Length(
              min=2,
              max=80,
              message='El apellido debe tener entre 2 y 80 caracteres.',
          ),
          Regexp(
              r'^[A-ZÁÉÍÓÚÑ][a-záéíóúñA-ZÁÉÍÓÚÑ\s]*$',
              message=(
                  'El apellido debe iniciar con mayúscula y contener únicamente'
                  ' letras.'
              ),
          ),
      ],
      render_kw={
          'placeholder': 'Ej. Pérez Gómez',
          'class': 'form-control bg-dark text-white border-secondary',
      },
  )

  username = StringField(
      'Nombre de Usuario',
      validators=[
          DataRequired(message='El nombre de usuario es obligatorio.'),
          Length(
              min=3, max=50, message='Debe tener entre 3 y 50 caracteres.'
          ),
          Regexp(
              r'^[a-zA-Z0-9_.-]+$',
              message='Solo letras, números, puntos y guiones.',
          ),
      ],
      render_kw={
          'placeholder': 'Ej. jperez',
          'class': 'form-control bg-dark text-white border-secondary',
      },
  )

  email = StringField(
      'Correo Electrónico',
      validators=[
          DataRequired(message='El correo es obligatorio.'),
          Email(message='Ingrese un correo válido.'),
      ],
      render_kw={
          'placeholder': 'correo@ejemplo.com',
          'class': 'form-control bg-dark text-white border-secondary',
      },
  )

  telefono = StringField(
      'Número de Contacto / Celular',
      validators=[
          DataRequired(message='El número de teléfono es obligatorio.'),
          Regexp(
              r'^[0-9]{7,10}$',
              message=(
                  'El teléfono debe contener únicamente números (entre 7 y 10'
                  ' dígitos).'
              ),
          ),
      ],
      render_kw={
          'placeholder': 'Ej. 0991234567',
          'class': 'form-control bg-dark text-white border-secondary',
          'maxlength': '10',
          'pattern': '[0-9]*',
          'inputmode': 'numeric',
          'oninput': "this.value = this.value.replace(/[^0-9]/g, '')",
      },
  )

  # Solo opción de Cliente para el registro público
  rol = SelectField(
      'Tipo de Cuenta (Rol)',
      choices=[
          ('Cliente', 'Cliente (Reservar citas, ver historial)'),
      ],
      default='Cliente',
      validators=[DataRequired(message='El rol es obligatorio.')],
      render_kw={
          'class': 'form-select bg-dark text-white border-secondary',
          'tabindex': '-1',
          'aria-disabled': 'true',
      },
  )

  password = PasswordField(
      'Contraseña',
      validators=[
          DataRequired(message='La contraseña es obligatoria.'),
          Length(min=6, message='Mínimo 6 caracteres.'),
      ],
      render_kw={
          'placeholder': 'Mínimo 6 caracteres',
          'class': 'form-control bg-dark text-white border-secondary',
      },
  )

  confirm_password = PasswordField(
      'Confirmar Contraseña',
      validators=[
          DataRequired(message='Confirme su contraseña.'),
          EqualTo('password', message='Las contraseñas no coinciden.'),
      ],
      render_kw={
          'placeholder': 'Repita la contraseña',
          'class': 'form-control bg-dark text-white border-secondary',
      },
  )

  captcha = StringField(
      'Código de Seguridad',
      validators=[
          DataRequired(message='Debe ingresar los caracteres de la imagen.')
      ],
      render_kw={
          'placeholder': 'Ingrese el texto de la imagen',
          'class': (
              'form-control bg-dark text-white border-secondary text-uppercase'
              ' text-center fw-bold'
          ),
          'autocomplete': 'off',
      },
  )

  submit = SubmitField(
      'Crear Cuenta',
      render_kw={'class': 'btn btn-warning fw-bold text-dark w-100 py-2'},
  )