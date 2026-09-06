import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, url_for, redirect, request, flash

# Importamos las clases de formularios desde la carpeta forms
from forms.producto_form import ProductoForm
from forms.cliente_form import ClienteForm
from forms.cita_form import CitaForm
from forms.facturacion_form import FacturaForm
from forms.proveedor_form import ProveedorForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta_barberia'

# ==========================================
# 1. CONFIGURACIÓN DE BASE DE DATOS SQLITE
# ==========================================
def get_db_connection():
    os.makedirs('data', exist_ok=True)
    conn = sqlite3.connect('data/barberia_hernandez.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    
    # Tabla Productos
    conn.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    ''')
    
    # Tabla Clientes
    conn.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            telefono TEXT NOT NULL,
            email TEXT NOT NULL
        )
    ''')

    # Tabla Citas
    conn.execute('''
        CREATE TABLE IF NOT EXISTS citas (
            id TEXT PRIMARY KEY,
            cliente TEXT NOT NULL,
            telefono TEXT NOT NULL,
            fecha TEXT NOT NULL,
            hora TEXT NOT NULL,
            barbero TEXT NOT NULL,
            servicio TEXT NOT NULL,
            estado TEXT NOT NULL
        )
    ''')

    # Tabla Proveedores
    conn.execute('''
        CREATE TABLE IF NOT EXISTS proveedores (
            ruc TEXT PRIMARY KEY,
            empresa TEXT NOT NULL,
            telefono TEXT NOT NULL,
            estado TEXT NOT NULL
        )
    ''')

    # Tabla Facturas
    conn.execute('''
        CREATE TABLE IF NOT EXISTS facturas (
            num TEXT PRIMARY KEY,
            cliente TEXT NOT NULL,
            metodo_pago TEXT NOT NULL,
            monto TEXT NOT NULL,
            estado TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

# Ejecutamos la creación de tablas al iniciar
init_db()


# ==========================================
# 2. RUTAS PRINCIPALES
# ==========================================
@app.route('/')
def home():
    return redirect(url_for('citas'))

@app.route('/index')
def index():
    return render_template('index.html')


# ==========================================
# 3. MÓDULO DE PRODUCTOS
# ==========================================
@app.route('/productos')
def productos():
    conn = get_db_connection()
    productos_db = conn.execute('SELECT * FROM productos').fetchall()
    conn.close()
    return render_template('productos.html', lista_productos=productos_db)

@app.route('/productos/nuevo', methods=['GET', 'POST'])
def nuevo_producto():
    form = ProductoForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO productos (nombre, precio, stock)
            VALUES (?, ?, ?)
        ''', (form.nombre.data, float(form.precio.data), int(form.stock.data)))
        conn.commit()
        conn.close()
        flash('¡Producto registrado con éxito!', 'success')
        return redirect(url_for('productos'))
    return render_template('formulario_producto.html', form=form)

@app.route('/productos/detalle/<int:id>')
def detalle_producto(id):
    conn = get_db_connection()
    producto_encontrado = conn.execute('SELECT * FROM productos WHERE id = ?', (id,)).fetchone()
    conn.close()
    return render_template('detalle_producto.html', producto=producto_encontrado)

@app.route('/productos/editar/<int:id>', methods=['GET', 'POST'])
def editar_producto(id):
    conn = get_db_connection()
    row = conn.execute('SELECT * FROM productos WHERE id = ?', (id,)).fetchone()
    
    if not row:
        conn.close()
        flash('Producto no encontrado.', 'danger')
        return redirect(url_for('productos'))
        
    producto_encontrado = dict(row)
    form = ProductoForm()
    
    if form.validate_on_submit():
        conn.execute('''
            UPDATE productos 
            SET nombre = ?, precio = ?, stock = ?
            WHERE id = ?
        ''', (form.nombre.data, float(form.precio.data), int(form.stock.data), id))
        conn.commit()
        conn.close()
        flash('¡Producto actualizado con éxito!', 'success')
        return redirect(url_for('productos'))
        
    elif request.method == 'GET':
        form.nombre.data = producto_encontrado['nombre']
        form.precio.data = producto_encontrado['precio']
        form.stock.data = producto_encontrado['stock']
        
    conn.close()
    return render_template('formulario_producto.html', form=form, editando=True)

@app.route('/productos/borrar/<int:id>')
def borrar_producto(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM productos WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('¡Producto eliminado!', 'warning')
    return redirect(url_for('productos'))

# ==========================================
# 4. MÓDULO DE CLIENTES
# ==========================================
@app.route('/clientes')
def clientes():
    conn = get_db_connection()
    clientes_db = conn.execute('SELECT * FROM clientes').fetchall()
    conn.close()
    return render_template('clientes.html', clientes=clientes_db)

@app.route('/clientes/nuevo', methods=['GET', 'POST'])
def formulario_cliente():
    form = ClienteForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        # Generar ID dinámico contando los registros actuales
        count = conn.execute('SELECT COUNT(*) FROM clientes').fetchone()[0]
        nuevo_id = f"CLI-{count + 1:03d}"
        
        conn.execute('''
            INSERT INTO clientes (id, nombre, apellido, telefono, email)
            VALUES (?, ?, ?, ?, ?)
        ''', (nuevo_id, form.nombre.data, form.apellido.data, form.telefono.data, form.email.data))
        conn.commit()
        conn.close()
        flash('¡Cliente registrado con éxito!', 'success')
        return redirect(url_for('clientes'))
    return render_template('formulario_cliente.html', form=form)

# --- RUTA PARA EL BOTÓN "VER" ---
@app.route('/clientes/detalle/<string:id>')
def detalle_cliente(id):
    conn = get_db_connection()
    row = conn.execute('SELECT * FROM clientes WHERE id = ?', (id,)).fetchone()
    conn.close()
    
    if not row:
        flash('Cliente no encontrado.', 'danger')
        return redirect(url_for('clientes'))
        
    return render_template('detalle_cliente.html', cliente=dict(row))
# --------------------------------

@app.route('/clientes/editar/<string:id>', methods=['GET', 'POST'])
def editar_cliente(id):
    conn = get_db_connection()
    row = conn.execute('SELECT * FROM clientes WHERE id = ?', (id,)).fetchone()

    if not row:
        conn.close()
        flash('Cliente no encontrado.', 'danger')
        return redirect(url_for('clientes'))

    cliente_encontrado = dict(row)
    form = ClienteForm()
    
    if form.validate_on_submit():
        conn.execute('''
            UPDATE clientes 
            SET nombre = ?, apellido = ?, telefono = ?, email = ?
            WHERE id = ?
        ''', (form.nombre.data, form.apellido.data, form.telefono.data, form.email.data, id))
        conn.commit()
        conn.close()
        flash('¡Cliente actualizado con éxito!', 'success')
        return redirect(url_for('clientes'))
    
    elif request.method == 'GET':
        form.nombre.data = cliente_encontrado.get('nombre', '')
        form.apellido.data = cliente_encontrado.get('apellido', '')
        form.telefono.data = cliente_encontrado.get('telefono', '')
        form.email.data = cliente_encontrado.get('email', '')

    conn.close()
    return render_template('formulario_cliente.html', form=form, editando=True)

@app.route('/clientes/eliminar/<string:id>')
def eliminar_cliente(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM clientes WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('¡Cliente eliminado con éxito!', 'warning')
    return redirect(url_for('clientes'))

# ==========================================
# 5. MÓDULO DE CITAS
# ==========================================
@app.route('/citas')
def citas():
    conn = get_db_connection()
    citas_db = conn.execute('SELECT * FROM citas').fetchall()
    conn.close()
    return render_template('citas.html', citas=citas_db)

@app.route('/citas/nueva', methods=['GET', 'POST'])
def formulario_cita():
    form = CitaForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        count = conn.execute('SELECT COUNT(*) FROM citas').fetchone()[0]
        nuevo_id = f"C-{count + 1:03d}" 
        
        barbero_str = dict(form.barbero.choices).get(form.barbero.data) if hasattr(form, 'barbero') else form.barbero.data
        servicio_str = dict(form.servicio.choices).get(form.servicio.data) if hasattr(form, 'servicio') else form.servicio.data

        conn.execute('''
            INSERT INTO citas (id, cliente, telefono, fecha, hora, barbero, servicio, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nuevo_id, form.cliente.data, form.telefono.data, form.fecha.data.strftime('%Y-%m-%d'),
              form.hora.data.strftime('%H:%M'), barbero_str, servicio_str, 'Pendiente'))
        
        conn.commit()
        conn.close()
        flash('¡Cita registrada con éxito!', 'success')
        return redirect(url_for('citas'))
    return render_template('formulario_cita.html', form=form)

@app.route('/citas/cambiar_estado/<string:id>')
def cambiar_estado_cita(id):
    conn = get_db_connection()
    row = conn.execute('SELECT estado FROM citas WHERE id = ?', (id,)).fetchone()
    if row:
        nuevo_estado = 'Pendiente' if row['estado'] == 'Confirmada' else 'Confirmada'
        conn.execute('UPDATE citas SET estado = ? WHERE id = ?', (nuevo_estado, id))
        conn.commit()
    conn.close()
    return redirect(url_for('citas'))

@app.route('/citas/editar/<string:id>', methods=['GET', 'POST'])
def editar_cita(id):
    conn = get_db_connection()
    row = conn.execute('SELECT * FROM citas WHERE id = ?', (id,)).fetchone()

    if not row:
        conn.close()
        flash('Cita no encontrada.', 'danger')
        return redirect(url_for('citas'))

    cita_encontrada = dict(row)
    form = CitaForm()
    
    if form.validate_on_submit():
        barbero_str = dict(form.barbero.choices).get(form.barbero.data) if hasattr(form, 'barbero') else form.barbero.data
        servicio_str = dict(form.servicio.choices).get(form.servicio.data) if hasattr(form, 'servicio') else form.servicio.data

        conn.execute('''
            UPDATE citas 
            SET cliente=?, telefono=?, fecha=?, hora=?, barbero=?, servicio=?
            WHERE id=?
        ''', (form.cliente.data, form.telefono.data, form.fecha.data.strftime('%Y-%m-%d'),
              form.hora.data.strftime('%H:%M'), barbero_str, servicio_str, id))
        conn.commit()
        conn.close()
        flash('¡Cita actualizada con éxito!', 'success')
        return redirect(url_for('citas'))
    
    elif request.method == 'GET':
        form.cliente.data = cita_encontrada.get('cliente', '')
        form.telefono.data = cita_encontrada.get('telefono', '')
        try:
            form.fecha.data = datetime.strptime(cita_encontrada['fecha'], '%Y-%m-%d').date()
        except (ValueError, KeyError):
            pass
        try:
            form.hora.data = datetime.strptime(cita_encontrada['hora'], '%H:%M').time()
        except (ValueError, KeyError):
            pass

    conn.close()
    return render_template('formulario_cita.html', form=form, editando=True)

@app.route('/citas/eliminar/<string:id>')
def eliminar_cita(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM citas WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('¡Cita eliminada con éxito!', 'warning')
    return redirect(url_for('citas'))


# ==========================================
# 6. MÓDULO DE PROVEEDORES
# ==========================================
HTML_PROVEEDOR_SEGURO = '''
{% extends "base.html" %}
{% block title %}{% if editando %}Editar Proveedor{% else %}Nuevo Proveedor{% endif %} - Barbería Hernández{% endblock %}
{% block content %}
<div class="container mt-5">
    <div class="mb-3">
        <h4 class="text-secondary fw-bold">Proveedores</h4>
    </div>
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card shadow border-dark">
                <div class="card-header bg-dark text-white text-center">
                    <h4 class="mb-0">
                        <i class="fas fa-truck"></i> {% if editando %}Editar Proveedor{% else %}Registrar Nuevo Proveedor{% endif %}
                    </h4>
                </div>
                <div class="card-body bg-light">
                    <form method="POST" action="" novalidate>
                        {{ form.hidden_tag() }}
                        
                        <div class="mb-3">
                            {{ form.ruc.label(class="form-label fw-bold text-dark") }}
                            {{ form.ruc(class="form-control " + ("is-invalid" if form.ruc.errors else ""), placeholder="Ej. 1790011223001") }}
                            {% for error in form.ruc.errors %}
                                <div class="invalid-feedback fw-bold text-danger d-block mt-1">{{ error }}</div>
                            {% endfor %}
                        </div>

                        <div class="mb-3">
                            {{ form.empresa.label(class="form-label fw-bold text-dark") }}
                            {{ form.empresa(class="form-control " + ("is-invalid" if form.empresa.errors else ""), placeholder="Ej. Distribuidora BarberXP") }}
                            {% for error in form.empresa.errors %}
                                <div class="invalid-feedback fw-bold text-danger d-block mt-1">{{ error }}</div>
                            {% endfor %}
                        </div>

                        <div class="mb-3">
                            {{ form.telefono.label(class="form-label fw-bold text-dark") }}
                            {{ form.telefono(class="form-control " + ("is-invalid" if form.telefono.errors else ""), placeholder="Ej. 022345678") }}
                            {% for error in form.telefono.errors %}
                                <div class="invalid-feedback fw-bold text-danger d-block mt-1">{{ error }}</div>
                            {% endfor %}
                        </div>

                        <div class="d-grid gap-2">
                            {{ form.submit(class="btn btn-dark btn-lg") }}
                            <a href="{{ url_for('proveedores') }}" class="btn btn-outline-secondary">Cancelar</a>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''

@app.route('/proveedores')
def proveedores():
    conn = get_db_connection()
    proveedores_db = conn.execute('SELECT * FROM proveedores').fetchall()
    conn.close()
    return render_template('proveedores.html', proveedores=proveedores_db)

@app.route('/proveedores/nuevo', methods=['GET', 'POST'])
def formulario_proveedor():
    from flask import render_template_string
    form = ProveedorForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        try:
            conn.execute('''
                INSERT INTO proveedores (ruc, empresa, telefono, estado)
                VALUES (?, ?, ?, ?)
            ''', (form.ruc.data, form.empresa.data, form.telefono.data, 'Activo'))
            conn.commit()
            flash('¡Proveedor registrado con éxito!', 'success')
        except sqlite3.IntegrityError:
            flash('El RUC ingresado ya existe en la base de datos.', 'danger')
        conn.close()
        return redirect(url_for('proveedores'))
    
    return render_template_string(HTML_PROVEEDOR_SEGURO, form=form, editando=False)

@app.route('/proveedores/editar/<string:ruc>', methods=['GET', 'POST'])
def editar_proveedor(ruc):
    from flask import render_template_string
    conn = get_db_connection()
    row = conn.execute('SELECT * FROM proveedores WHERE ruc = ?', (ruc,)).fetchone()

    if not row:
        conn.close()
        flash('Proveedor no encontrado.', 'danger')
        return redirect(url_for('proveedores'))

    proveedor_encontrado = dict(row)
    form = ProveedorForm()
    
    if form.validate_on_submit():
        conn.execute('''
            UPDATE proveedores 
            SET empresa = ?, telefono = ?
            WHERE ruc = ?
        ''', (form.empresa.data, form.telefono.data, ruc))
        conn.commit()
        conn.close()
        flash('¡Proveedor actualizado con éxito!', 'success')
        return redirect(url_for('proveedores'))
    
    elif request.method == 'GET':
        form.ruc.data = proveedor_encontrado.get('ruc', '')
        form.empresa.data = proveedor_encontrado.get('empresa', '')
        form.telefono.data = proveedor_encontrado.get('telefono', '')

    conn.close()
    return render_template_string(HTML_PROVEEDOR_SEGURO, form=form, editando=True)

@app.route('/proveedores/eliminar/<string:ruc>')
def eliminar_proveedor(ruc):
    conn = get_db_connection()
    conn.execute('DELETE FROM proveedores WHERE ruc = ?', (ruc,))
    conn.commit()
    conn.close()
    flash('¡Proveedor eliminado con éxito!', 'warning')
    return redirect(url_for('proveedores'))

@app.route('/proveedores/cambiar_estado/<string:ruc>')
def cambiar_estado_proveedor(ruc):
    conn = get_db_connection()
    row = conn.execute('SELECT estado FROM proveedores WHERE ruc = ?', (ruc,)).fetchone()
    if row:
        nuevo_estado = 'Inactivo' if row['estado'] == 'Activo' else 'Activo'
        conn.execute('UPDATE proveedores SET estado = ? WHERE ruc = ?', (nuevo_estado, ruc))
        conn.commit()
    conn.close()
    return redirect(url_for('proveedores'))


# ==========================================
# 7. MÓDULO DE FACTURACIÓN
# ==========================================
@app.route('/facturacion')
def facturacion():
    conn = get_db_connection()
    facturas_db = conn.execute('SELECT * FROM facturas').fetchall()
    conn.close()
    return render_template('facturacion.html', facturas=facturas_db)

@app.route('/facturacion/nueva', methods=['GET', 'POST'])
def nueva_factura():
    form = FacturaForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        count = conn.execute('SELECT COUNT(*) FROM facturas').fetchone()[0]
        nuevo_num = f"FAC-00{count + 1}"
        
        conn.execute('''
            INSERT INTO facturas (num, cliente, metodo_pago, monto, estado)
            VALUES (?, ?, ?, ?, ?)
        ''', (nuevo_num, form.cliente.data, form.metodo_pago.data, "$25.00", form.estado.data))
        conn.commit()
        conn.close()
        flash('¡Factura registrada con éxito!', 'success')
        return redirect(url_for('facturacion'))
    return render_template('formulario_facturacion.html', form=form)

@app.route('/facturacion/cambiar_estado/<string:num>')
def cambiar_estado_factura(num):
    conn = get_db_connection()
    row = conn.execute('SELECT estado FROM facturas WHERE num = ?', (num,)).fetchone()
    if row:
        nuevo_estado = 'Pendiente' if row['estado'] == 'Pagado' else 'Pagado'
        conn.execute('UPDATE facturas SET estado = ? WHERE num = ?', (nuevo_estado, num))
        conn.commit()
    conn.close()
    return redirect(url_for('facturacion'))

@app.route('/facturacion/detalle/<string:num>')
def detalle_factura(num):
    conn = get_db_connection()
    factura_encontrada = conn.execute('SELECT * FROM facturas WHERE num = ?', (num,)).fetchone()
    conn.close()
    return render_template('detalle_factura.html', factura=factura_encontrada)

@app.route('/facturacion/editar/<string:num>', methods=['GET', 'POST'])
def editar_factura(num):
    conn = get_db_connection()
    row = conn.execute('SELECT * FROM facturas WHERE num = ?', (num,)).fetchone()
            
    if not row:
        conn.close()
        flash('Factura no encontrada.', 'danger')
        return redirect(url_for('facturacion'))
        
    factura_encontrada = dict(row)
    form = FacturaForm()
    
    if form.validate_on_submit():
        conn.execute('''
            UPDATE facturas 
            SET cliente = ?, metodo_pago = ?, estado = ?
            WHERE num = ?
        ''', (form.cliente.data, form.metodo_pago.data, form.estado.data, num))
        conn.commit()
        conn.close()
        flash('¡Factura actualizada con éxito!', 'success')
        return redirect(url_for('facturacion'))
        
    elif request.method == 'GET':
        form.cliente.data = factura_encontrada['cliente']
        form.metodo_pago.data = factura_encontrada['metodo_pago']
        form.estado.data = factura_encontrada['estado']
        
    conn.close()
    return render_template('formulario_facturacion.html', form=form)

@app.route('/facturacion/borrar/<string:num>')
def borrar_factura(num):
    conn = get_db_connection()
    conn.execute('DELETE FROM facturas WHERE num = ?', (num,))
    conn.commit()
    conn.close()
    flash('¡Factura eliminada correctamente!', 'warning')
    return redirect(url_for('facturacion'))

if __name__ == '__main__':
    app.run(debug=True)