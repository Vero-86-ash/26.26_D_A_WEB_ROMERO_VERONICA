from datetime import time
from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
    TimeField,
)
from wtforms.validators import DataRequired, Length, Optional, Regexp, ValidationError


class CitaForm(FlaskForm):
  cliente = StringField(
      'Nombre del Cliente',
      validators=[
          DataRequired(message='El nombre del cliente es obligatorio.'),
          Regexp(
              r'^[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)+$',
              message=(
                  'Debe ingresar nombre y apellido, y cada uno debe iniciar con'
                  ' mayúscula.'
              ),
          ),
      ],
  )

  telefono = StringField(
      'Teléfono de Contacto',
      validators=[
          DataRequired(message='El teléfono es necesario.'),
          Length(min=7, max=10, message='Ingrese un número de 7 a 10 dígitos.'),
          Regexp(
              r'^[0-9]+$',
              message=(
                  'El número telefónico debe contener únicamente números sin'
                  ' espacios ni guiones.'
              ),
          ),
      ],
  )

  fecha = DateField(
      'Fecha de la Cita',
      format='%Y-%m-%d',
      validators=[DataRequired(message='Debe seleccionar una fecha.')],
  )

  hora = TimeField(
      'Hora de la Cita',
      format='%H:%M',
      validators=[DataRequired(message='Debe seleccionar una hora.')],
  )

  # IDs numéricos correspondientes a cada barbero en la base de datos
  barbero = SelectField(
      'Seleccione su Barbero',
      choices=[
          ('', '--- Seleccione ---'),
          ('1', 'Andrés Hernández'),
          ('2', 'Mateo Romero'),
          ('3', 'Ariel Hernández'),
      ],
      validators=[DataRequired(message='Debe elegir un barbero.')],
  )

  servicio = SelectField(
      'Servicio Principal',
      choices=[
          ('', '--- Seleccione ---'),
          ('Corte de Cabello', 'Corte de Cabello'),
          ('Perfilado de Barba', 'Perfilado de Barba'),
          ('Corte de Cabello + Barba', 'Corte de Cabello + Barba'),
          ('Tinte y Limpieza Facial', 'Tinte y Limpieza Facial'),
      ],
      validators=[DataRequired(message='Debe elegir un servicio.')],
  )

  # Campo para notas del cliente
  notas_cliente = TextAreaField(
      'Notas o Peticiones Especiales (Opcional)', validators=[Optional()]
  )

  submit = SubmitField('Agendar Cita')

  # Validación de Horario de Atención: 09:00 AM a 09:00 PM
  def validate_hora(self, field):
    if field.data:
      hora_inicio = time(9, 0)  # 09:00 AM
      hora_fin = time(21, 0)  # 09:00 PM
      if field.data < hora_inicio or field.data > hora_fin:
        raise ValidationError(
            'El horario de atención es exclusivamente de 09:00 AM a 09:00 PM.'
        )