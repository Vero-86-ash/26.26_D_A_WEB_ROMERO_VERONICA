from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    DecimalField,
    SelectField,
    IntegerField,
    TextAreaField,
    SubmitField,
)
from wtforms.validators import DataRequired, Optional, NumberRange, Length


class FacturaForm(FlaskForm):
    # 1. Número de Factura: Soporte para ambos identificadores (numero_factura y num_factura)
    numero_factura = StringField(
        'Nº de Factura (Secuencial Automático)',
        render_kw={
            'readonly': True,
            'class': 'form-control bg-dark text-warning border-secondary fw-bold',
            'placeholder': '001-001-000001'
        }
    )

    num_factura = StringField(
        'Nº de Factura (Secuencial Automático)',
        render_kw={
            'readonly': True,
            'class': 'form-control bg-dark text-warning border-secondary fw-bold',
            'placeholder': '001-001-000001'
        }
    )

    # 2. Tipo de Operación
    tipo_operacion = SelectField(
        'Tipo de Operación',
        choices=[
            ('Venta', 'Venta comercial (Cliente - Ingreso)'),
            ('Compra', 'Compra de inventario / insumos (Proveedor - Egreso)')
        ],
        default='Venta',
        validators=[DataRequired(message="Seleccione el tipo de operación.")]
    )

    # 3. Receptor (Cliente o Proveedor)
    cliente_id = SelectField(
        'Seleccionar Cliente Registrado',
        coerce=int,
        validators=[Optional()]
    )
    proveedor_ruc = SelectField(
        'Seleccionar Proveedor',
        validators=[Optional()]
    )

    cliente = StringField(
        'Nombre del Cliente / Razón Social',
        validators=[
            Optional(),
            Length(min=2, max=150, message="El nombre debe tener entre 2 y 150 caracteres.")
        ]
    )
    identificacion = StringField(
        'Cédula o RUC',
        validators=[
            Optional(),
            Length(min=10, max=13, message="La identificación debe tener entre 10 y 13 dígitos.")
        ]
    )

    # 4. Ítem a Facturar (Servicio o Producto)
    tipo_item = SelectField(
        'Tipo de Ítem',
        choices=[
            ('Servicio', 'Servicio de Barbería (Corte, Barba, Tratamientos)'),
            ('Producto', 'Producto de Inventario (Pomadas, Aceites, Accesorios)')
        ],
        default='Servicio',
        validators=[DataRequired()]
    )

    servicio_id = SelectField('Seleccionar Servicio', coerce=int, validators=[Optional()])
    producto_id = SelectField('Seleccionar Producto', coerce=int, validators=[Optional()])

    descripcion_concepto = TextAreaField(
        'Descripción / Detalle del Concepto',
        validators=[
            Optional(),
            Length(max=255, message="La descripción no puede exceder los 255 caracteres.")
        ]
    )
    cantidad = IntegerField(
        'Cantidad',
        default=1,
        validators=[
            DataRequired(message="La cantidad es obligatoria."),
            NumberRange(min=1, message="La cantidad mínima es 1.")
        ]
    )

    # 5. Valores Financieros (Soporta impuestos e iva)
    precio_unitario = DecimalField(
        'Precio Unitario ($)',
        default=0.00,
        places=2,
        validators=[
            Optional(),
            NumberRange(min=0.00, message="El precio unitario no puede ser negativo.")
        ]
    )
    subtotal = DecimalField(
        'Subtotal ($)',
        default=0.00,
        places=2,
        validators=[
            DataRequired(message="El subtotal es obligatorio."),
            NumberRange(min=0.00, message="El subtotal no puede ser negativo.")
        ]
    )
    impuestos = DecimalField(
        'Impuestos / IVA ($)',
        default=0.00,
        places=2,
        validators=[
            Optional(),
            NumberRange(min=0.00, message="Los impuestos no pueden ser negativos.")
        ]
    )
    iva = DecimalField(
        'IVA (15%) ($)',
        default=0.00,
        places=2,
        validators=[
            Optional(),
            NumberRange(min=0.00, message="El IVA no puede ser negativo.")
        ]
    )
    descuento = DecimalField(
        'Descuento ($)',
        default=0.00,
        places=2,
        validators=[
            Optional(),
            NumberRange(min=0.00, message="El descuento no puede ser negativo.")
        ]
    )
    total = DecimalField(
        'Total a Pagar ($)',
        default=0.00,
        places=2,
        validators=[
            DataRequired(message="El total es obligatorio."),
            NumberRange(min=0.00, message="El total no puede ser negativo.")
        ]
    )

    # 6. Método de Pago
    metodo_pago = SelectField(
        'Método de Pago',
        choices=[
            ('Efectivo', 'Efectivo'),
            ('Transferencia', 'Transferencia Bancaria'),
            ('Tarjeta de Débito', 'Tarjeta de Débito'),
            ('Tarjeta de Crédito', 'Tarjeta de Crédito'),
            ('Deuna / QR', 'Deuna / Pago con QR')
        ],
        default='Efectivo',
        validators=[DataRequired(message="Seleccione un método de pago.")]
    )

    referencia_pago = StringField(
        'Nº de Referencia / Comprobante',
        validators=[
            Optional(),
            Length(max=100, message="La referencia no puede exceder los 100 caracteres.")
        ]
    )

    # 7. Estado
    estado = SelectField(
        'Estado del Registro',
        choices=[
            ('Activo', 'Activo / Emitida'),
            ('Inactivo', 'Inactivo / Anulada')
        ],
        default='Activo',
        validators=[DataRequired()]
    )

    # 8. Botón de envío
    submit = SubmitField(
        'Guardar Factura',
        render_kw={'class': 'btn btn-primary fw-bold px-4'}
    )