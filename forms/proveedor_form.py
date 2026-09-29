from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp, Email, NumberRange

class ProveedorForm(FlaskForm):
    ruc = StringField("RUC / Identificación", validators=[
        DataRequired(message="El RUC es obligatorio."),
        Length(min=10, max=13, message="El RUC debe tener exactamente entre 10 y 13 dígitos."),
        Regexp(r'^\d+$', message="El RUC debe contener estrictamente solo números (sin letras).")
    ])
    
    empresa = StringField("Nombre de la Empresa", validators=[
        DataRequired(message="El nombre de la empresa es obligatorio."),
        Length(min=3, max=100, message="El nombre debe tener al menos 3 caracteres."),
        Regexp(r'^(?!\s)(?!.*[\s-]{2})[a-zA-ZáéíóúÁÉÍÓÚñÑ0-9\s\.\,\-]+(?<!\s)$', 
                message="Ingrese un nombre de empresa válido (evite texto aleatorio o símbolos inválidos).")
    ])
    
    telefono = StringField("Teléfono de la Empresa", validators=[
        DataRequired(message="El teléfono es obligatorio."),
        Length(min=7, max=15, message="El teléfono debe tener entre 7 y 15 dígitos."),
        Regexp(r'^\d+$', message="El teléfono debe contener estrictamente solo números (sin letras).")
    ])
    
    email = StringField("Correo Electrónico", validators=[
        DataRequired(message="El correo es obligatorio."),
        Email(message="El correo debe tener un formato válido (ejemplo: usuario@dominio.com)"),
        Regexp(r'^[\w\.-]+@[\w\.-]+\.com$', message="El correo electrónico debe terminar obligatoriamente en .com")
    ])

    direccion = StringField("Dirección", validators=[
        DataRequired(message="La dirección es obligatoria.")
    ])

    ciudad = StringField("Ciudad", validators=[
        DataRequired(message="La ciudad es obligatoria.")
    ])

    nombre_contacto = StringField("Nombre de Contacto", validators=[
        DataRequired(message="El nombre de contacto es obligatorio.")
    ])

    telefono_contacto = StringField("Teléfono de Contacto", validators=[
        DataRequired(message="El teléfono de contacto es obligatorio."),
        Length(min=7, max=15, message="El teléfono de contacto debe tener entre 7 y 15 dígitos."),
        Regexp(r'^\d+$', message="El teléfono de contacto debe contener estrictamente solo números.")
    ])

    dias_credito = IntegerField("Días de Crédito", validators=[
        DataRequired(message="Los días de crédito son obligatorios."),
        NumberRange(min=0, message="Los días de crédito deben ser un número positivo.")
    ])
    
    submit = SubmitField("Guardar Proveedor")