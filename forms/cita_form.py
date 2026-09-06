from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TimeField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp

class CitaForm(FlaskForm):
    cliente = StringField('Nombre del Cliente', validators=[
        DataRequired(message="El nombre del cliente es obligatorio."),
        Regexp(r'^[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)+$', 
               message="Debe ingresar nombre y apellido, y cada uno debe iniciar con mayúscula.")
    ])
    
    telefono = StringField('Teléfono de Contacto', validators=[
        DataRequired(message="El teléfono es necesario."),
        Length(min=7, max=10, message="Ingrese un número de 7 a 10 dígitos."),
        Regexp(r'^[0-9]+$', 
               message="El número telefónico debe contener únicamente números sin espacios ni guiones.")
    ])
    
    fecha = DateField('Fecha de la Cita', format='%Y-%m-%d', validators=[
        DataRequired(message="Debe seleccionar una fecha.")
    ])
    
    hora = TimeField('Hora de la Cita', format='%H:%M', validators=[
        DataRequired(message="Debe seleccionar una hora.")
    ])
    
    barbero = SelectField('Seleccione su Barbero', choices=[
        ('', '--- Seleccione ---'),
        ('Andres Hernández', 'Andrés Hernández'),
        ('Mateo Romero', 'Mateo Romero'),
        ('Ariel Hernández', 'Ariel Hernández')
    ], validators=[DataRequired(message="Debe elegir un barbero.")])
    
    servicio = SelectField('Servicio Principal', choices=[
        ('', '--- Seleccione ---'),
        ('Corte de Cabello', 'Corte de Cabello'),
        ('Perfilado de Barba', 'Perfilado de Barba'),
        ('Corte de Cabello + Barba', 'Corte de Cabello + Barba'),
        ('Tinte y Limpieza Facial', 'Tinte y Limpieza Facial')
    ], validators=[DataRequired(message="Debe elegir un servicio.")])
    
    submit = SubmitField('Agendar Cita')