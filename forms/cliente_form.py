from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp, Email

class ClienteForm(FlaskForm):
    nombre = StringField("Nombre", validators=[
        DataRequired(message="El nombre es obligatorio."),
        Length(min=2, max=50, message="Debe tener entre 2 y 50 caracteres."),
        Regexp(r'^[A-ZÁÉÍÓÚÑ][a-záéíóúñÁÉÍÓÚÑ\s]*$', message="El nombre debe iniciar obligatoriamente con una letra mayúscula y contener solo letras.")
    ])
    
    apellido = StringField("Apellido", validators=[
        DataRequired(message="El apellido es obligatorio."),
        Length(min=2, max=50, message="Debe tener entre 2 y 50 caracteres."),
        Regexp(r'^[A-ZÁÉÍÓÚÑ][a-záéíóúñÁÉÍÓÚÑ\s]*$', message="El apellido debe iniciar obligatoriamente con una letra mayúscula y contener solo letras.")
    ])
    
    telefono = StringField("Teléfono de Contacto", validators=[
        DataRequired(message="El teléfono es obligatorio."),
        Length(min=7, max=15, message="Debe tener entre 7 y 15 dígitos."),
        Regexp(r'^\d+$', message="El teléfono debe contener estrictamente solo números (sin letras).")
    ])
    
    email = StringField("Correo Electrónico", validators=[
        DataRequired(message="El correo es obligatorio."),
        Email(message="Ingrese un correo válido."),
        Regexp(r'^[\w\.-]+@[\w\.-]+\.com$', message="El correo debe contener '@' y terminar obligatoriamente en '.com'.")
    ])
    
    submit = SubmitField("Guardar Cliente")