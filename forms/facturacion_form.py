from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Regexp

class FacturaForm(FlaskForm):
    cliente = StringField('Nombre y Apellido del Cliente', validators=[
        DataRequired(message="El nombre del cliente es obligatorio."),
        Regexp(r'^[A-ZÁÉÍÓÚÑ][a-zA-ZáéíóúñÁÉÍÓÚÑ]+(\s[A-ZÁÉÍÓÚÑ][a-zA-ZáéíóúñÁÉÍÓÚÑ]+)+$', 
               message="Debe ingresar Nombre y Apellido, y cada uno debe iniciar con mayúscula (ej. Carlos Mendoza).")
    ])
    
    metodo_pago = SelectField('Método de Pago', choices=[
        ('', '--- Seleccione Método ---'),
        ('Efectivo', 'Efectivo'),
        ('Tarjeta de Crédito/Débito', 'Tarjeta de Crédito/Débito'),
        ('Transferencia', 'Transferencia')
    ], validators=[DataRequired(message="Debe seleccionar un método de pago.")])
    
    estado = SelectField('Estado de Factura', choices=[
        ('Pagado', 'Pagado'),
        ('Pendiente', 'Pendiente')
    ], validators=[DataRequired(message="Debe seleccionar el estado.")])
    
    submit = SubmitField('Generar Factura')