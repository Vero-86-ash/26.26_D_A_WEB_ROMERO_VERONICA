from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp

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
    
    telefono = StringField("Teléfono de Contacto", validators=[
        DataRequired(message="El teléfono es obligatorio."),
        Length(min=7, max=15, message="El teléfono debe tener entre 7 y 15 dígitos."),
        Regexp(r'^\d+$', message="El teléfono debe contener estrictamente solo números (sin letras).")
    ])
    
    submit = SubmitField("Guardar Proveedor")