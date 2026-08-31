from flask import Flask, render_template, url_for, redirect, request, flash

# Importamos las clases de formularios desde la carpeta forms
from forms.producto_form import ProductoForm
from forms.cliente_form import ClienteForm
from forms.cita_form import CitaForm
from forms.facturacion_form import FacturaForm
from forms.proveedor_form import ProveedorForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta_barberia'

# --- LISTAS GLOBALES DE LOS MÓDULOS ---

lista_productos = [
    {"id": "PROD-001", "nombre": "Cera modeladora", "precio": 8.50, "stock": 15},
    {"id": "PROD-002", "nombre": "Aceite para barba", "precio": 12.00, "stock": 4}
]

lista_clientes = [
    {"id": 1, "nombre": "Carlos", "apellido": "Mendoza", "telefono": "0998765432", "email": "carlos@gmail.com"},
    {"id": 2, "nombre": "Andrés", "apellido": "Silva", "telefono": "0981234567", "email": "andres@gmail.com"},
]

lista_citas = [
    {"id": 1, "cliente": "Carlos Mendoza", "barbero": "Andres Hernández", "servicio": "Corte de Cabello + Barba", "fecha": "2026-08-15", "hora": "10:00 AM", "estado": "Confirmada"},
    {"id": 2, "cliente": "Andrés Silva", "barbero": "Mateo Romero", "servicio": "Perfilado de Barba", "fecha": "2026-08-15", "hora": "11:30 AM", "estado": "Pendiente"},
    {"id": 3, "cliente": "Juan Pérez", "barbero": "Ariel Hernández", "servicio": "Tinte y Limpieza Facial", "fecha": "2026-08-16", "hora": "03:00 PM", "estado": "Confirmada"}
]

lista_proveedores = [
    {"ruc": "1790011223001", "empresa": "Distribuidora BarberXP", "telefono": "022345678", "estado": "Activo"},
    {"ruc": "1790044556001", "empresa": "Cosméticos Style Ecuador", "telefono": "022987654", "estado": "Activo"}
]

lista_facturas = [
    {"num": "FAC-001", "cliente": "Carlos Mendoza", "metodo_pago": "Efectivo", "monto": "$27.50", "estado": "Pagado"},
    {"num": "FAC-002", "cliente": "Andrés Silva", "metodo_pago": "Transferencia", "monto": "$15.50", "estado": "Pendiente"}
]

# --- RUTAS PRINCIPALES ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/index1')
def index1():
    return render_template('index1.html')


    # --- MÓDULO DE CLIENTES ---

@app.route('/clientes')
def clientes():
    return render_template('clientes.html', lista_clientes=lista_clientes)

@app.route('/clientes/nuevo', methods=['GET', 'POST'])
def nuevo_cliente():
    form = ClienteForm()
    if form.validate_on_submit():
        nuevo = {
            'id': len(lista_clientes) + 1,
            'nombre': form.nombre.data,
            'apellido': form.apellido.data,
            'telefono': form.telefono.data,
            'email': form.email.data
        }
        lista_clientes.append(nuevo)
        flash('¡Cliente registrado con éxito!', 'success')
        return redirect(url_for('clientes'))
    
    return render_template('formulario_cliente.html', form=form)

# --->  BOTÓN ELIMINAR <---
@app.route('/clientes/borrar/<int:id>')
def borrar_cliente(id):
    global lista_clientes
    lista_clientes = [c for c in lista_clientes if c['id'] != id]
    flash('¡Cliente eliminado correctamente!', 'warning')
    return redirect(url_for('clientes'))
    return render_template('clientes.html', lista_clientes=lista_clientes)


# --- MÓDULO DE PRODUCTOS ---
@app.route('/productos')
def productos():
    return render_template('productos.html', lista_productos=lista_productos)

@app.route('/productos/nuevo', methods=['GET', 'POST'])
def nuevo_producto():
    form = ProductoForm()
    if form.validate_on_submit():
        nuevo = {
            'id': f"PROD-00{len(lista_productos) + 1}",
            'nombre': form.nombre.data,
            'precio': float(form.precio.data),
            'stock': int(form.stock.data)
        }
        lista_productos.append(nuevo)
        flash('¡Producto registrado con éxito!', 'success')
        return redirect(url_for('productos'))
    return render_template('formulario_producto.html', form=form)

@app.route('/productos/detalle/<string:id>')
def detalle_producto(id):
    producto_encontrado = None
    for p in lista_productos:
        if str(p['id']) == id:
            producto_encontrado = p
            break
    return render_template('detalle_producto.html', producto=producto_encontrado)

@app.route('/productos/editar/<string:id>', methods=['GET', 'POST'])
def editar_producto(id):
    producto_encontrado = None
    for p in lista_productos:
        if str(p['id']) == id:
            producto_encontrado = p
            break
    if not producto_encontrado:
        return redirect(url_for('productos'))
        
    form = ProductoForm()
    if form.validate_on_submit():
        producto_encontrado['nombre'] = form.nombre.data
        producto_encontrado['precio'] = float(form.precio.data)
        producto_encontrado['stock'] = int(form.stock.data)
        flash('¡Producto actualizado con éxito!', 'success')
        return redirect(url_for('productos'))
        
    if request.method == 'GET':
        form.nombre.data = producto_encontrado['nombre']
        form.precio.data = producto_encontrado['precio']
        form.stock.data = producto_encontrado['stock']
        
    return render_template('formulario_producto.html', form=form)

@app.route('/productos/borrar/<string:id>')
def borrar_producto(id):
    global lista_productos
    lista_productos = [p for p in lista_productos if str(p['id']) != id]
    flash('¡Producto eliminado!', 'warning')
    return redirect(url_for('productos'))


# --- MÓDULO DE CITAS ---
@app.route('/citas')
def citas():
    return render_template('citas.html', citas=lista_citas)

@app.route('/citas/nueva', methods=['GET', 'POST'])
def formulario_cita():
    form = CitaForm()
    if form.validate_on_submit():
        nuevo_id = f"C-{len(lista_citas) + 1:03d}" 
        nueva_cita = {
            'id': nuevo_id,
            'cliente': form.cliente.data,
            'telefono': form.telefono.data,
            'fecha': form.fecha.data.strftime('%Y-%m-%d'),
            'hora': form.hora.data.strftime('%H:%M'),
            'barbero': dict(form.barbero.choices).get(form.barbero.data),
            'servicio': dict(form.servicio.choices).get(form.servicio.data),
            'estado': 'Pendiente'
        }
        lista_citas.append(nueva_cita)
        flash('¡Cita registrada con éxito!', 'success')
        return redirect(url_for('citas'))
    return render_template('formulario_cita.html', form=form)

@app.route('/citas/cambiar_estado/<string:id>')
def cambiar_estado_cita(id):
    for cita in lista_citas:
        if str(cita['id']) == id:
            if cita['estado'] == 'Confirmada':
                cita['estado'] = 'Pendiente'
            else:
                cita['estado'] = 'Confirmada'
            break 
    return redirect(url_for('citas'))


# --- MÓDULO DE PROVEEDORES ---
@app.route('/proveedores')
def proveedores():
    return render_template('proveedores.html', proveedores=lista_proveedores)

@app.route('/proveedores/nuevo', methods=['GET', 'POST'])
def formulario_proveedor():
    form = ProveedorForm()
    if form.validate_on_submit():
        nuevo_proveedor = {
            'ruc': form.ruc.data,
            'empresa': form.empresa.data,
            'telefono': form.telefono.data,
            'estado': 'Activo'
        }
        lista_proveedores.append(nuevo_proveedor)
        flash('¡Proveedor registrado con éxito!', 'success')
        return redirect(url_for('proveedores'))
    
    return render_template('formulario_producto.html', form=form)

@app.route('/proveedores/cambiar_estado/<string:ruc>')
def cambiar_estado_proveedor(ruc):
    for prov in lista_proveedores:
        if str(prov['ruc']) == ruc:
            prov['estado'] = 'Inactivo' if prov['estado'] == 'Activo' else 'Activo'
            break
    return redirect(url_for('proveedores'))


# --- MÓDULO DE FACTURACIÓN ---
@app.route('/facturacion')
def facturacion():
    return render_template('facturacion.html', facturas=lista_facturas)

@app.route('/facturacion/nueva', methods=['GET', 'POST'])
def nueva_factura():
    form = FacturaForm()
    if form.validate_on_submit():
        nueva = {
            'num': f"FAC-00{len(lista_facturas) + 1}",
            'cliente': form.cliente.data, 
            'metodo_pago': form.metodo_pago.data,
            'monto': "$25.00", 
            'estado': form.estado.data
        }
        lista_facturas.append(nueva)
        flash('¡Factura registrada con éxito!', 'success')
        return redirect(url_for('facturacion'))
    return render_template('formulario_facturacion.html', form=form)

@app.route('/facturacion/cambiar_estado/<string:num>')
def cambiar_estado_factura(num):
    for f in lista_facturas:
        if str(f['num']) == num:
            f['estado'] = 'Pendiente' if f['estado'] == 'Pagado' else 'Pagado'
            break
    return redirect(url_for('facturacion'))

@app.route('/facturacion/detalle/<string:num>')
def detalle_factura(num):
    factura_encontrada = None
    for f in lista_facturas:
        if str(f['num']) == num:
            factura_encontrada = f
            break
    return render_template('detalle_factura.html', factura=factura_encontrada)


if __name__ == '__main__':
    app.run(debug=True)