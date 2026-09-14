from flask import Flask, render_template, url_for, redirect, request, flash
from conexion.conexion import get_db_connection
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

# Importamos las clases de formularios desde la carpeta forms
from forms.producto_form import ProductoForm
from forms.cliente_form import ClienteForm
from forms.cita_form import CitaForm
from forms.facturacion_form import FacturaForm
from forms.proveedor_form import ProveedorForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta_barberia'

# ==========================================
# RUTAS PRINCIPALES
# ==========================================
@app.route('/')
def home():
    return redirect(url_for('productos'))

@app.route('/index')
def index():
    return render_template('index.html')

# ==========================================
# 1. MÓDULO DE PRODUCTOS (PostgreSQL)
# ==========================================
@app.route('/productos')
def productos():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM productos ORDER BY id ASC')
    productos_db = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('productos.html', lista_productos=productos_db)

@app.route('/productos/nuevo', methods=['GET', 'POST'])
def nuevo_producto():
    form = ProductoForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        cursor = conn.cursor()
        # Se envía 0.00 a costo_compra para cumplir con la regla NOT NULL de tu base de datos
        cursor.execute('''
            INSERT INTO productos (nombre, precio, stock, costo_compra)
            VALUES (%s, %s, %s, %s)
        ''', (form.nombre.data, float(form.precio.data), int(form.stock.data), 0.00))
        conn.commit()
        cursor.close()
        conn.close()
        flash('¡Producto registrado con éxito!', 'success')
        return redirect(url_for('productos'))
    return render_template('formulario_producto.html', form=form)

@app.route('/productos/detalle/<int:id>')
def detalle_producto(id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM productos WHERE id = %s', (id,))
    producto_encontrado = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('detalle_producto.html', producto=producto_encontrado)

@app.route('/productos/editar/<int:id>', methods=['GET', 'POST'])
def editar_producto(id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM productos WHERE id = %s', (id,))
    producto_encontrado = cursor.fetchone()
    
    if not producto_encontrado:
        cursor.close()
        conn.close()
        flash('Producto no encontrado.', 'danger')
        return redirect(url_for('productos'))
        
    form = ProductoForm()
    if form.validate_on_submit():
        cursor.execute('''
            UPDATE productos 
            SET nombre = %s, precio = %s, stock = %s
            WHERE id = %s
        ''', (form.nombre.data, float(form.precio.data), int(form.stock.data), id))
        conn.commit()
        cursor.close()
        conn.close()
        flash('¡Producto actualizado con éxito!', 'success')
        return redirect(url_for('productos'))
        
    elif request.method == 'GET':
        form.nombre.data = producto_encontrado['nombre']
        form.precio.data = producto_encontrado['precio']
        form.stock.data = producto_encontrado['stock']
        
    cursor.close()
    conn.close()
    return render_template('formulario_producto.html', form=form, editando=True)

@app.route('/productos/borrar/<int:id>')
def borrar_producto(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM productos WHERE id = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('¡Producto eliminado!', 'warning')
    return redirect(url_for('productos'))

# ==========================================
# 2. MÓDULO DE CLIENTES (PostgreSQL)
# ==========================================
@app.route('/clientes')
def clientes():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM clientes ORDER BY id ASC')
    clientes_db = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('clientes.html', clientes=clientes_db)

@app.route('/clientes/nuevo', methods=['GET', 'POST'])
def formulario_cliente():
    form = ClienteForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO clientes (nombre, apellido, telefono, email)
            VALUES (%s, %s, %s, %s)
        ''', (form.nombre.data, form.apellido.data, form.telefono.data, form.email.data))
        conn.commit()
        cursor.close()
        conn.close()
        flash('¡Cliente registrado con éxito!', 'success')
        return redirect(url_for('clientes'))
    return render_template('formulario_cliente.html', form=form)

@app.route('/clientes/detalle/<int:id>')
def detalle_cliente(id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM clientes WHERE id = %s', (id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not row:
        flash('Cliente no encontrado.', 'danger')
        return redirect(url_for('clientes'))
        
    return render_template('detalle_cliente.html', cliente=row)

@app.route('/clientes/editar/<int:id>', methods=['GET', 'POST'])
def editar_cliente(id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM clientes WHERE id = %s', (id,))
    cliente_encontrado = cursor.fetchone()

    if not cliente_encontrado:
        cursor.close()
        conn.close()
        flash('Cliente no encontrado.', 'danger')
        return redirect(url_for('clientes'))

    form = ClienteForm()
    if form.validate_on_submit():
        cursor.execute('''
            UPDATE clientes 
            SET nombre = %s, apellido = %s, telefono = %s, email = %s
            WHERE id = %s
        ''', (form.nombre.data, form.apellido.data, form.telefono.data, form.email.data, id))
        conn.commit()
        cursor.close()
        conn.close()
        flash('¡Cliente actualizado con éxito!', 'success')
        return redirect(url_for('clientes'))
    
    elif request.method == 'GET':
        form.nombre.data = cliente_encontrado['nombre']
        form.apellido.data = cliente_encontrado['apellido']
        form.telefono.data = cliente_encontrado['telefono']
        form.email.data = cliente_encontrado['email']

    cursor.close()
    conn.close()
    return render_template('formulario_cliente.html', form=form, editando=True)

@app.route('/clientes/eliminar/<int:id>')
def eliminar_cliente(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM clientes WHERE id = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('¡Cliente eliminado con éxito!', 'warning')
    return redirect(url_for('clientes'))

# ==========================================
# 3. MÓDULO DE PROVEEDORES (PostgreSQL)
# ==========================================
@app.route('/proveedores')
def proveedores():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM proveedores ORDER BY ruc ASC')
    proveedores_db = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('proveedores.html', proveedores=proveedores_db)

@app.route('/proveedores/nuevo', methods=['GET', 'POST'])
def formulario_proveedor():
    form = ProveedorForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO proveedores (ruc, empresa, telefono)
                VALUES (%s, %s, %s)
            ''', (form.ruc.data, form.empresa.data, form.telefono.data))
            conn.commit()
            flash('¡Proveedor registrado con éxito!', 'success')
        except psycopg2.IntegrityError:
            conn.rollback()
            flash('El RUC ingresado ya existe en la base de datos.', 'danger')
        cursor.close()
        conn.close()
        return redirect(url_for('proveedores'))
    
    return render_template('formulario_proveedores.html', form=form, editando=False)

@app.route('/proveedores/editar/<string:ruc>', methods=['GET', 'POST'])
def editar_proveedor(ruc):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM proveedores WHERE ruc = %s', (ruc,))
    proveedor_encontrado = cursor.fetchone()

    if not proveedor_encontrado:
        cursor.close()
        conn.close()
        flash('Proveedor no encontrado.', 'danger')
        return redirect(url_for('proveedores'))

    form = ProveedorForm()
    if form.validate_on_submit():
        cursor.execute('''
            UPDATE proveedores 
            SET empresa = %s, telefono = %s
            WHERE ruc = %s
        ''', (form.empresa.data, form.telefono.data, ruc))
        conn.commit()
        cursor.close()
        conn.close()
        flash('¡Proveedor actualizado con éxito!', 'success')
        return redirect(url_for('proveedores'))
    
    elif request.method == 'GET':
        form.ruc.data = proveedor_encontrado['ruc']
        form.empresa.data = proveedor_encontrado['empresa']
        form.telefono.data = proveedor_encontrado['telefono']

    cursor.close()
    conn.close()
    return render_template('formulario_proveedores.html', form=form, editando=True)

@app.route('/proveedores/eliminar/<string:ruc>')
def eliminar_proveedor(ruc):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM proveedores WHERE ruc = %s', (ruc,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('¡Proveedor eliminado con éxito!', 'warning')
    return redirect(url_for('proveedores'))

if __name__ == '__main__':
    app.run(debug=True)