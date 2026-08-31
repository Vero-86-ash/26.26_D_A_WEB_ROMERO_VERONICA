from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Regexp, NumberRange

class ProductoForm(FlaskForm):
    nombre = StringField('Nombre del Producto', validators=[
        DataRequired(message="El nombre del producto es obligatorio."),
        Regexp(r'^[A-ZÁÉÍÓÚÑ][a-zA-ZáéíóúñÁÉÍÓÚÑ0-9\s]+$', 
               message="El nombre debe iniciar con una letra mayúscula.")
    ])
    
    precio = DecimalField('Precio ($)', places=2, validators=[
        DataRequired(message="El precio es obligatorio."),
        NumberRange(min=0.01, message="El precio debe ser mayor a 0.")
    ])
    
    stock = IntegerField('Stock / Cantidad', validators=[
        DataRequired(message="El stock es obligatorio."),
        NumberRange(min=0, message="El stock no puede ser negativo.")
    ])
    
    submit = SubmitField('Guardar Producto')
  
    