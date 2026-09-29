from flask_wtf import FlaskForm
from wtforms import DecimalField, IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional, Regexp

class ProductoForm(FlaskForm):
    codigo_barras = StringField('Código de Barras', validators=[
        Optional()
    ])

    nombre = StringField('Nombre del Producto', validators=[
        DataRequired(message="El nombre del producto es obligatorio."),
        Regexp(
            r'^[A-ZÁÉÍÓÚÑ][a-zA-ZáéíóúñÁÉÍÓÚÑ0-9\s\.\-\(\)\/]+$', 
            message="El nombre debe iniciar con una letra mayúscula."
        )
    ])
    
    precio = DecimalField('Precio de Venta ($)', places=2, validators=[
        DataRequired(message="El precio es obligatorio."),
        NumberRange(min=0.01, message="El precio de venta debe ser mayor a 0.")
    ])

    costo = DecimalField('Costo de Compra ($)', places=2, validators=[
        Optional(),
        NumberRange(min=0.0, message="El costo no puede ser negativo.")
    ])
    
    stock = IntegerField('Stock Disponible', validators=[
        DataRequired(message="El stock es obligatorio."),
        NumberRange(min=0, message="El stock no puede ser negativo.")
    ])

    stock_minimo = IntegerField('Stock Mínimo', default=3, validators=[
        Optional(),
        NumberRange(min=0, message="El stock mínimo no puede ser negativo.")
    ])

    unidad_medida = StringField('Unidad de Medida', default='Unidad', validators=[
        Optional()
    ])

    imagen_url = StringField('URL de la Imagen', validators=[
        Optional()
    ])
    
    submit = SubmitField('Guardar Producto')