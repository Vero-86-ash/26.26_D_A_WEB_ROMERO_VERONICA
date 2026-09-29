import datetime
from datetime import datetime as dt, time
from functools import wraps
import io
import math
import os
import random

from captcha.image import ImageCaptcha
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

# Conexión a la base de datos (PostgreSQL / Render)
from conexion.conexion import get_db_connection

# Formularios del sistema
from forms.cita_form import CitaForm
from forms.cliente_form import ClienteForm
from forms.facturacion_form import FacturaForm
from forms.login_form import LoginForm
from forms.perfil_form import PerfilUsuarioForm
from forms.producto_form import ProductoForm
from forms.proveedor_form import ProveedorForm
from forms.usuario_form import UsuarioRegistroForm

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'clave_secreta_barberia')

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE SUBIDA DE IMÁGENES DE PRODUCTOS
# -----------------------------------------------------------------------------
UPLOAD_FOLDER = os.path.join('static', 'uploads', 'productos')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(os.path.join(app.root_path, UPLOAD_FOLDER), exist_ok=True)


def allowed_file(filename):
    return (
        '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    )


# -----------------------------------------------------------------------------
# CATÁLOGOS GLOBALES DE BARBEROS Y SERVICIOS
# -----------------------------------------------------------------------------
BARBEROS_MAP = {
    1: 'Andrés Hernández',
    2: 'Mateo Romero',
    3: 'Ariel Hernández',
    '1': 'Andrés Hernández',
    '2': 'Mateo Romero',
    '3': 'Ariel Hernández',
}

SERVICIOS_MAP = {
    1: 'Corte de Cabello',
    2: 'Arreglo de Barba Clásica',
    3: 'Cuidado y Limpieza Facial',
    4: 'Combo Completo (Corte + Barba + Facial)',
    '1': 'Corte de Cabello',
    '2': 'Arreglo de Barba Clásica',
    '3': 'Cuidado y Limpieza Facial',
    '4': 'Combo Completo (Corte + Barba + Facial)',
    'Corte de Cabello': 'Corte de Cabello',
    'Arreglo de Barba Clásica': 'Arreglo de Barba Clásica',
    'Perfilado de Barba': 'Arreglo de Barba Clásica',
    'Cuidado y Limpieza Facial': 'Cuidado y Limpieza Facial',
    'Tinte y Limpieza Facial': 'Cuidado y Limpieza Facial',
    'Combo Completo (Corte + Barba + Facial)': (
        'Combo Completo (Corte + Barba + Facial)'
    ),
}

app.jinja_env.globals.update(BARBEROS=BARBEROS_MAP, SERVICIOS=SERVICIOS_MAP)


# -----------------------------------------------------------------------------
# SERVICIO Y RUTA DINÁMICA DE CAPTCHA
# -----------------------------------------------------------------------------
def generar_codigo_captcha(longitud=5):
    caracteres = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ'
    return ''.join(random.choice(caracteres) for _ in range(longitud))


@app.route('/captcha/<formulario>')
def servir_captcha(formulario):
    codigo = generar_codigo_captcha()
    session[f'captcha_{formulario}'] = codigo

    generador = ImageCaptcha(width=180, height=55)
    datos_imagen = generador.generate(codigo)

    buffer = io.BytesIO()
    buffer.write(datos_imagen.getvalue())
    buffer.seek(0)

    return send_file(buffer, mimetype='image/png')


# -----------------------------------------------------------------------------
# DECORADORES DE PROTECCIÓN DE RUTAS POR SESIÓN Y ROL
# -----------------------------------------------------------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Inicie sesión para acceder a esta sección.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Inicie sesión para continuar.', 'warning')
            return redirect(url_for('login'))
        if session.get('rol') != 'Administrador':
            flash('Acceso restringido: requiere permisos de Administrador.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


# -----------------------------------------------------------------------------
# RUTAS DE AUTENTICACIÓN Y GESTIÓN DE PERFIL
# -----------------------------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'usuario_id' in session:
        return redirect(url_for('dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        captcha_ingresado = (
            form.captcha.data.strip().upper()
            if hasattr(form, 'captcha') and form.captcha.data
            else ''
        )
        captcha_esperado = session.get('captcha_login', '')

        if not captcha_esperado or captcha_ingresado != captcha_esperado:
            flash('El código CAPTCHA es incorrecto. Inténtelo nuevamente.', 'danger')
            return render_template('login.html', form=form)

        identificador = form.email.data.strip().lower()
        password = form.password.data

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute(
            """
            SELECT * FROM usuarios 
            WHERE (email = %s OR username = %s) AND estado = 'Activo'
            """,
            (identificador, identificador),
        )
        usuario = cursor.fetchone()

        if usuario and check_password_hash(usuario['password_hash'], password):
            session['usuario_id'] = usuario['id']
            session['usuario_nombre'] = usuario['nombre_completo']
            session['rol'] = usuario['rol']
            session.pop('captcha_login', None)

            if usuario['rol'] == 'Cliente':
                cursor.execute(
                    'SELECT telefono FROM clientes WHERE usuario_id = %s LIMIT 1',
                    (usuario['id'],),
                )
                cliente_reg = cursor.fetchone()
                if cliente_reg and cliente_reg.get('telefono'):
                    session['usuario_telefono'] = cliente_reg['telefono']

            cursor.execute(
                'UPDATE usuarios SET ultimo_acceso = CURRENT_TIMESTAMP WHERE id = %s',
                (usuario['id'],),
            )
            conn.commit()
            cursor.close()
            conn.close()

            flash(f'¡Bienvenido/a {usuario["nombre_completo"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            cursor.close()
            conn.close()
            flash('Credenciales incorrectas o cuenta inactiva.', 'danger')

    return render_template('login.html', form=form)


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if 'usuario_id' in session:
        return redirect(
            url_for('citas' if session.get('rol') == 'Cliente' else 'dashboard')
        )

    form = UsuarioRegistroForm()
    if form.validate_on_submit():
        captcha_ingresado = (
            form.captcha.data.strip().upper()
            if hasattr(form, 'captcha') and form.captcha.data
            else ''
        )
        captcha_esperado = session.get('captcha_registro', '')

        if not captcha_esperado or captcha_ingresado != captcha_esperado:
            flash('El código CAPTCHA de registro es incorrecto.', 'danger')
            return render_template('registro.html', form=form)

        cedula = (
            form.cedula.data.strip()
            if hasattr(form, 'cedula') and form.cedula.data
            else None
        )
        nombre = form.nombre.data.strip()
        apellido = form.apellido.data.strip()
        username = form.username.data.strip().lower()
        nombre_completo = f'{nombre} {apellido}'.strip()
        email = form.email.data.strip().lower()
        telefono = (
            form.telefono.data.strip()
            if hasattr(form, 'telefono') and form.telefono.data
            else None
        )

        rol = 'Cliente'
        hash_pass = generate_password_hash(
            form.password.data, method='scrypt', salt_length=16
        )

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        try:
            cursor.execute(
                'SELECT id FROM usuarios WHERE email = %s OR username = %s',
                (email, username),
            )
            if cursor.fetchone():
                flash(
                    'El correo electrónico o nombre de usuario ya se encuentra registrado.',
                    'danger',
                )
                return render_template('registro.html', form=form)

            if cedula:
                cursor.execute(
                    "SELECT id FROM clientes WHERE cedula = %s AND estado = 'Activo'",
                    (cedula,),
                )
                if cursor.fetchone():
                    flash(
                        'El número de cédula ingresado ya pertenece a un cliente registrado.',
                        'danger',
                    )
                    return render_template('registro.html', form=form)

            cursor.execute(
                """
                INSERT INTO usuarios (nombre_completo, username, email, password_hash, rol, estado)
                VALUES (%s, %s, %s, %s, %s, 'Activo')
                RETURNING id
                """,
                (nombre_completo, username, email, hash_pass, rol),
            )
            nuevo_usuario_id = cursor.fetchone()['id']

            cursor.execute(
                """
                INSERT INTO clientes (
                    usuario_id, cedula, nombre, apellido, email, telefono, 
                    preferencias, puntos_fidelidad, estado
                )
                VALUES (%s, %s, %s, %s, %s, %s, 'Ninguna', 0, 'Activo')
                """,
                (nuevo_usuario_id, cedula, nombre, apellido, email, telefono),
            )

            conn.commit()
            session.pop('captcha_registro', None)

            session['usuario_id'] = nuevo_usuario_id
            session['usuario_nombre'] = nombre_completo
            session['rol'] = rol
            if telefono:
                session['usuario_telefono'] = telefono

            flash(
                f'¡Bienvenido/a {nombre_completo}! Tu cuenta ha sido creada exitosamente.',
                'success',
            )
            return redirect(url_for('formulario_cita'))

        except psycopg2.IntegrityError as ie:
            conn.rollback()
            print('Error de integridad al registrar:', ie)
            flash(
                'Error: la cédula, correo o teléfono ya están asociados a otra cuenta.',
                'danger',
            )
        except Exception as e:
            conn.rollback()
            print('Error SQL en registro automático:', e)
            flash(f'Ocurrió un error inesperado al crear la cuenta: {e}', 'danger')
        finally:
            cursor.close()
            conn.close()

    return render_template('registro.html', form=form)


@app.route('/mi-perfil', methods=['GET', 'POST'])
@login_required
def mi_perfil():
    form = PerfilUsuarioForm()
    usuario_id = session.get('usuario_id')
    rol = session.get('rol')

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    if request.method == 'GET':
        cursor.execute(
            """
            SELECT u.nombre_completo, u.email, c.nombre, c.apellido, c.telefono
            FROM usuarios u
            LEFT JOIN clientes c ON c.usuario_id = u.id
            WHERE u.id = %s
            """,
            (usuario_id,),
        )
        datos = cursor.fetchone()

        if datos:
            if datos['nombre']:
                form.nombre.data = datos['nombre']
                form.apellido.data = datos['apellido'] or ''
                form.telefono.data = datos['telefono'] or ''
            else:
                partes = (datos['nombre_completo'] or '').split(' ', 1)
                form.nombre.data = partes[0]
                form.apellido.data = partes[1] if len(partes) > 1 else ''

    if form.validate_on_submit():
        nombre = form.nombre.data.strip()
        apellido = form.apellido.data.strip()
        telefono = form.telefono.data.strip() if form.telefono.data else None
        nombre_completo = f'{nombre} {apellido}'.strip()

        try:
            cursor.execute(
                """
                UPDATE usuarios 
                SET nombre_completo = %s 
                WHERE id = %s
                """,
                (nombre_completo, usuario_id),
            )

            if rol == 'Cliente':
                cursor.execute(
                    'SELECT id FROM clientes WHERE usuario_id = %s', (usuario_id,)
                )
                existe_cliente = cursor.fetchone()
                if existe_cliente:
                    cursor.execute(
                        """
                        UPDATE clientes 
                        SET nombre = %s, apellido = %s, telefono = %s 
                        WHERE usuario_id = %s
                        """,
                        (nombre, apellido, telefono, usuario_id),
                    )
                else:
                    cursor.execute(
                        """
                        INSERT INTO clientes (nombre, apellido, telefono, usuario_id, estado)
                        VALUES (%s, %s, %s, %s, 'Activo')
                        """,
                        (nombre, apellido, telefono, usuario_id),
                    )

            conn.commit()
            session['usuario_nombre'] = nombre_completo
            if telefono:
                session['usuario_telefono'] = telefono
            flash(
                '¡Tus datos personales se han actualizado correctamente!', 'success'
            )
            return redirect(url_for('mi_perfil'))

        except Exception as e:
            conn.rollback()
            flash(f'Ocurrió un error al guardar los cambios: {e}', 'danger')
        finally:
            cursor.close()
            conn.close()

    cursor.close()
    conn.close()
    return render_template('perfil.html', form=form)


@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('login'))


# -----------------------------------------------------------------------------
# RUTAS PRINCIPALES Y DASHBOARD (CON EVENTOS Y ACTIVIDAD RECIENTE)
# -----------------------------------------------------------------------------
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/dashboard')
@login_required
def dashboard():
    rol = session.get('rol', 'Cliente')
    usuario_id = session.get('usuario_id')
    nombre = session.get('usuario_nombre')

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    eventos_recientes = []

    try:
        if rol == 'Administrador':
            cursor.execute("""
                SELECT 
                    'cita' AS tipo,
                    c.id,
                    'Cita: ' || c.servicio AS titulo,
                    COALESCE(cl.nombre || ' ' || COALESCE(cl.apellido, ''), u.nombre_completo, 'Cliente General') AS detalle,
                    c.fecha::text || ' ' || c.hora::text AS tiempo,
                    c.estado
                FROM citas c
                LEFT JOIN clientes cl ON c.cliente_id = cl.id
                LEFT JOIN usuarios u ON cl.usuario_id = u.id
                ORDER BY c.id DESC
                LIMIT 5
            """)
            citas_recientes = cursor.fetchall()

            cursor.execute("""
                SELECT 
                    'factura' AS tipo,
                    f.id,
                    'Factura ' || COALESCE(f.numero_factura, f.num_factura, '#' || f.id::text) AS titulo,
                    'Monto: $' || TO_CHAR(f.total, 'FM999990.00') || ' (' || COALESCE(f.metodo_pago, 'Efectivo') || ')' AS detalle,
                    COALESCE(f.fecha::text, 'Reciente') AS tiempo,
                    f.estado
                FROM facturas f
                ORDER BY f.id DESC
                LIMIT 5
            """)
            facturas_recientes = cursor.fetchall()

            eventos_recientes = citas_recientes + facturas_recientes
            eventos_recientes.sort(key=lambda x: x['id'], reverse=True)
            eventos_recientes = eventos_recientes[:7]

        else:
            cursor.execute("""
                SELECT 
                    'cita' AS tipo,
                    c.id,
                    'Turno reservado: ' || c.servicio AS titulo,
                    'Fecha: ' || c.fecha::text || ' a las ' || c.hora::text AS detalle,
                    c.fecha::text AS tiempo,
                    c.estado
                FROM citas c
                LEFT JOIN clientes cl ON c.cliente_id = cl.id
                WHERE cl.usuario_id = %s OR c.cliente_id IN (SELECT id FROM clientes WHERE usuario_id = %s)
                ORDER BY c.id DESC
                LIMIT 4
            """, (usuario_id, usuario_id))
            citas_usuario = cursor.fetchall()

            cursor.execute("""
                SELECT 
                    'factura' AS tipo,
                    f.id,
                    'Comprobante ' || COALESCE(f.numero_factura, f.num_factura, '#' || f.id::text) AS titulo,
                    'Total: $' || TO_CHAR(f.total, 'FM999990.00') AS detalle,
                    COALESCE(f.fecha::text, 'Reciente') AS tiempo,
                    f.estado
                FROM facturas f
                WHERE f.usuario_id = %s OR f.cliente_id = %s
                ORDER BY f.id DESC
                LIMIT 4
            """, (usuario_id, usuario_id))
            facturas_usuario = cursor.fetchall()

            eventos_recientes = citas_usuario + facturas_usuario
            eventos_recientes.sort(key=lambda x: x['id'], reverse=True)

    except Exception as e:
        print("Error al cargar eventos del dashboard:", e)
        eventos_recientes = []
    finally:
        cursor.close()
        conn.close()

    return render_template(
        'dashboard.html',
        rol=rol,
        nombre=nombre,
        eventos=eventos_recientes,
    )


# =============================================================================
# 1. MÓDULO DE CLIENTES (PostgreSQL)
# =============================================================================
@app.route('/clientes')
@login_required
@admin_required
def clientes():
    busqueda = request.args.get('q', '').strip()
    try:
        pagina = int(request.args.get('page', 1))
        if pagina < 1:
            pagina = 1
    except (ValueError, TypeError):
        pagina = 1

    por_pagina = 8
    offset = (pagina - 1) * por_pagina

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    param_busqueda = f'%{busqueda}%'

    try:
        cursor.execute(
            """
            SELECT *, COUNT(*) OVER() AS total_count
            FROM clientes
            WHERE estado = 'Activo'
              AND (
                  nombre ILIKE %s OR 
                  apellido ILIKE %s OR 
                  COALESCE(cedula, '') ILIKE %s OR 
                  COALESCE(telefono, '') ILIKE %s OR 
                  COALESCE(email, '') ILIKE %s
              )
            ORDER BY id DESC
            LIMIT %s OFFSET %s
            """,
            (
                param_busqueda,
                param_busqueda,
                param_busqueda,
                param_busqueda,
                param_busqueda,
                por_pagina,
                offset,
            ),
        )

        clientes_db = cursor.fetchall()
        total_registros = clientes_db[0]['total_count'] if clientes_db else 0
        total_paginas = max(1, math.ceil(total_registros / por_pagina))

    except Exception as e:
        print(f'Error al listar clientes: {e}')
        flash('No se pudo cargar la lista de clientes.', 'danger')
        clientes_db = []
        total_registros = 0
        total_paginas = 1
    finally:
        cursor.close()
        conn.close()

    return render_template(
        'clientes.html',
        clientes=clientes_db,
        busqueda=busqueda,
        pagina_actual=pagina,
        total_paginas=total_paginas,
        total_registros=total_registros,
        endpoint='clientes',
    )


@app.route('/clientes/nuevo', methods=['GET', 'POST'], endpoint='nuevo_cliente')
@app.route(
    '/clientes/formulario',
    methods=['GET', 'POST'],
    endpoint='formulario_cliente',
)
@login_required
@admin_required
def nuevo_cliente():
    form = ClienteForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cedula = (
                form.cedula.data.strip()
                if hasattr(form, 'cedula') and form.cedula.data
                else None
            )
            nombre = form.nombre.data.strip()
            apellido = form.apellido.data.strip()
            telefono = (
                form.telefono.data.strip()
                if hasattr(form, 'telefono') and form.telefono.data
                else None
            )
            email = (
                form.email.data.strip().lower()
                if hasattr(form, 'email') and form.email.data
                else None
            )

            if cedula:
                cursor.execute(
                    "SELECT id FROM clientes WHERE cedula = %s AND estado = 'Activo'",
                    (cedula,),
                )
                if cursor.fetchone():
                    flash(
                        'Ya existe un cliente activo registrado con esa cédula.',
                        'warning',
                    )
                    return render_template(
                        'formulario_cliente.html', form=form, titulo='Nuevo Cliente'
                    )

            cursor.execute(
                """
                INSERT INTO clientes (cedula, nombre, apellido, telefono, email, estado)
                VALUES (%s, %s, %s, %s, %s, 'Activo')
                RETURNING id
                """,
                (cedula, nombre, apellido, telefono, email),
            )

            conn.commit()
            flash('¡Cliente registrado con éxito en el sistema!', 'success')
            return redirect(url_for('clientes'))

        except psycopg2.IntegrityError as ie:
            conn.rollback()
            print(f'Violación de integridad: {ie}')
            flash(
                'Error: Cédula, teléfono o correo ya registrados en la base de datos.',
                'danger',
            )
        except Exception as e:
            conn.rollback()
            print(f'Error SQL al registrar cliente: {e}')
            flash(
                f'Ocurrió un error inesperado al registrar el cliente: {e}', 'danger'
            )
        finally:
            cursor.close()
            conn.close()

    return render_template(
        'formulario_cliente.html', form=form, titulo='Nuevo Cliente'
    )


@app.route('/clientes/detalle/<int:id>')
@login_required
@admin_required
def detalle_cliente(id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(
            "SELECT * FROM clientes WHERE id = %s AND estado = 'Activo'", (id,)
        )
        row = cursor.fetchone()

        if not row:
            flash(
                'El cliente solicitado no existe o se encuentra inactivo.', 'warning'
            )
            return redirect(url_for('clientes'))

        cursor.execute(
            """
            SELECT id, barbero_id, servicio, fecha, hora, estado
            FROM citas
            WHERE cliente_id = %s
            ORDER BY fecha DESC, hora DESC
            LIMIT 5
            """,
            (id,),
        )
        citas_cliente = cursor.fetchall()
        for c in citas_cliente:
            c['barbero'] = BARBEROS_MAP.get(c.get('barbero_id'), 'Andrés Hernández')

    except Exception as e:
        print(f'Error al obtener detalle del cliente: {e}')
        flash('Error al consultar los datos del cliente.', 'danger')
        return redirect(url_for('clientes'))
    finally:
        cursor.close()
        conn.close()

    return render_template(
        'detalle_cliente.html', cliente=row, historial_citas=citas_cliente
    )


@app.route('/clientes/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_cliente(id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute(
            "SELECT * FROM clientes WHERE id = %s AND estado = 'Activo'", (id,)
        )
        cliente_encontrado = cursor.fetchone()

        if not cliente_encontrado:
            flash('El cliente que desea editar no fue encontrado.', 'warning')
            return redirect(url_for('clientes'))

        form = ClienteForm()

        if form.validate_on_submit():
            cedula = (
                form.cedula.data.strip()
                if hasattr(form, 'cedula') and form.cedula.data
                else None
            )
            nombre = form.nombre.data.strip()
            apellido = form.apellido.data.strip()
            telefono = (
                form.telefono.data.strip()
                if hasattr(form, 'telefono') and form.telefono.data
                else None
            )
            email = (
                form.email.data.strip().lower()
                if hasattr(form, 'email') and form.email.data
                else None
            )

            if cedula:
                cursor.execute(
                    'SELECT id FROM clientes WHERE cedula = %s AND id != %s AND estado = \'Activo\'',
                    (cedula, id),
                )
                if cursor.fetchone():
                    flash(
                        'La cédula ingresada ya pertenece a otro cliente registrado.',
                        'warning',
                    )
                    return render_template(
                        'formulario_cliente.html', form=form, titulo='Editar Cliente'
                    )

            cursor.execute(
                """
                UPDATE clientes 
                SET cedula = %s, nombre = %s, apellido = %s, telefono = %s, email = %s
                WHERE id = %s
                """,
                (cedula, nombre, apellido, telefono, email, id),
            )

            conn.commit()
            flash('¡Información del cliente actualizada con éxito!', 'success')
            return redirect(url_for('clientes'))

        elif request.method == 'GET':
            if hasattr(form, 'cedula'):
                form.cedula.data = cliente_encontrado.get('cedula') or ''
            form.nombre.data = cliente_encontrado['nombre']
            form.apellido.data = cliente_encontrado['apellido']
            form.telefono.data = cliente_encontrado['telefono'] or ''
            form.email.data = cliente_encontrado['email'] or ''

    except Exception as e:
        conn.rollback()
        print(f'Error al editar cliente: {e}')
        flash(
            f'Ocurrió un error al intentar actualizar el cliente: {e}', 'danger'
        )
    finally:
        cursor.close()
        conn.close()

    return render_template(
        'formulario_cliente.html', form=form, titulo='Editar Cliente'
    )


@app.route('/clientes/eliminar/<int:id>', methods=['POST', 'GET'])
@login_required
@admin_required
def eliminar_cliente(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE clientes SET estado = 'Inactivo' WHERE id = %s", (id,)
        )
        conn.commit()
        flash('¡Cliente deshabilitado correctamente del sistema!', 'warning')
    except Exception as e:
        conn.rollback()
        print(f'Error al deshabilitar cliente: {e}')
        flash(f'No se pudo deshabilitar el cliente: {e}', 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('clientes'))


# -----------------------------------------------------------------------------
# 2. GESTIÓN DE PRODUCTOS, CATÁLOGO Y BUSCADOR (LUPITA)
# -----------------------------------------------------------------------------
@app.route('/productos')
@app.route('/catalogo')
@login_required
def productos():
    rol = session.get('rol', 'Cliente')
    busqueda = request.args.get('q', '').strip()

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        if rol == 'Administrador':
            query = """
                SELECT p.*, COALESCE(c.nombre, 'General') AS categoria
                FROM productos p
                LEFT JOIN categorias c ON p.categoria_id = c.id
                WHERE 1=1
            """
            params = []
            if busqueda:
                query += """ AND (
                    p.nombre ILIKE %s OR 
                    COALESCE(p.codigo_barras, '') ILIKE %s OR 
                    COALESCE(c.nombre, '') ILIKE %s
                )"""
                p_term = f"%{busqueda}%"
                params = [p_term, p_term, p_term]

            query += " ORDER BY p.id ASC"
            cursor.execute(query, tuple(params))
            items = cursor.fetchall()
            return render_template(
                'productos.html', 
                productos=items, 
                lista_productos=items,
                busqueda=busqueda
            )
        else:
            query = """
                SELECT p.*, COALESCE(c.nombre, 'General') AS categoria
                FROM productos p
                LEFT JOIN categorias c ON p.categoria_id = c.id
                WHERE p.estado = 'Activo' AND p.stock > 0
            """
            params = []
            if busqueda:
                query += """ AND (
                    p.nombre ILIKE %s OR 
                    COALESCE(p.codigo_barras, '') ILIKE %s OR 
                    COALESCE(c.nombre, '') ILIKE %s
                )"""
                p_term = f"%{busqueda}%"
                params = [p_term, p_term, p_term]

            query += " ORDER BY p.id ASC"
            cursor.execute(query, tuple(params))
            items = cursor.fetchall()
            return render_template(
                'productos_cliente.html', 
                productos=items, 
                lista_productos=items,
                busqueda=busqueda
            )
    finally:
        cursor.close()
        conn.close()


@app.route('/productos/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def nuevo_producto():
    form = ProductoForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            nombre = form.nombre.data.strip()
            precio = float(form.precio.data)
            stock = int(form.stock.data)
            costo = (
                float(form.costo.data)
                if hasattr(form, 'costo') and form.costo.data is not None
                else 0.00
            )

            if (
                hasattr(form, 'codigo_barras')
                and form.codigo_barras.data
                and form.codigo_barras.data.strip()
            ):
                codigo_barras = form.codigo_barras.data.strip()
            else:
                codigo_barras = f'786{random.randint(1000, 9999)}'

            stock_minimo = (
                int(form.stock_minimo.data)
                if hasattr(form, 'stock_minimo') and form.stock_minimo.data is not None
                else 3
            )
            unidad_medida = (
                form.unidad_medida.data.strip()
                if hasattr(form, 'unidad_medida') and form.unidad_medida.data
                else 'Unidad'
            )

            imagen = 'https://images.unsplash.com/photo-1597854710119-a5a84396736a?w=600'
            archivo_imagen = request.files.get('archivo_imagen')

            if (
                archivo_imagen
                and archivo_imagen.filename != ''
                and allowed_file(archivo_imagen.filename)
            ):
                nombre_seguro = secure_filename(archivo_imagen.filename)
                nombre_final = (
                    f'prod_{random.randint(10000, 99999)}_{nombre_seguro}'
                )
                ruta_guardado = os.path.join(
                    app.root_path, app.config['UPLOAD_FOLDER'], nombre_final
                )
                archivo_imagen.save(ruta_guardado)
                imagen = url_for(
                    'static', filename=f'uploads/productos/{nombre_final}'
                )
            elif (
                hasattr(form, 'imagen_url')
                and form.imagen_url.data
                and form.imagen_url.data.strip()
            ):
                imagen = form.imagen_url.data.strip()

            cursor.execute(
                """
                INSERT INTO productos (
                    codigo_barras, nombre, precio, costo, stock, 
                    stock_minimo, unidad_medida, imagen_url, estado
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Activo')
                """,
                (
                    codigo_barras,
                    nombre,
                    precio,
                    costo,
                    stock,
                    stock_minimo,
                    unidad_medida,
                    imagen,
                ),
            )

            conn.commit()
            flash('¡Producto registrado y guardado con éxito!', 'success')
            return redirect(url_for('productos'))

        except Exception as e:
            conn.rollback()
            print(f'Error SQL al registrar producto: {e}')
            flash(f'Ocurrió un error al registrar el producto: {e}', 'danger')
        finally:
            cursor.close()
            conn.close()

    elif request.method == 'POST':
        for campo, errores in form.errors.items():
            flash(f"Error en {campo}: {', '.join(errores)}", 'danger')

    return render_template('formulario_producto.html', form=form, editando=False)


@app.route('/productos/detalle/<int:id>')
@login_required
@admin_required
def detalle_producto(id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute('SELECT * FROM productos WHERE id = %s', (id,))
        producto_encontrado = cursor.fetchone()
        if not producto_encontrado:
            flash('Producto no encontrado.', 'warning')
            return redirect(url_for('productos'))
        return render_template(
            'detalle_producto.html', producto=producto_encontrado
        )
    finally:
        cursor.close()
        conn.close()


@app.route('/productos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_producto(id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute('SELECT * FROM productos WHERE id = %s', (id,))
        producto_encontrado = cursor.fetchone()

        if not producto_encontrado:
            flash('Producto no encontrado.', 'danger')
            return redirect(url_for('productos'))

        form = ProductoForm()

        if form.validate_on_submit():
            nombre = form.nombre.data.strip()
            precio = float(form.precio.data)
            costo = (
                float(form.costo.data)
                if hasattr(form, 'costo') and form.costo.data is not None
                else float(producto_encontrado.get('costo') or 0.0)
            )
            stock = int(form.stock.data)
            stock_minimo = (
                int(form.stock_minimo.data)
                if hasattr(form, 'stock_minimo') and form.stock_minimo.data is not None
                else 3
            )
            unidad = (
                form.unidad_medida.data.strip()
                if hasattr(form, 'unidad_medida') and form.unidad_medida.data
                else 'Unidad'
            )
            codigo = (
                form.codigo_barras.data.strip()
                if hasattr(form, 'codigo_barras') and form.codigo_barras.data
                else producto_encontrado.get('codigo_barras')
            )
            nuevo_estado = request.form.get(
                'estado', producto_encontrado.get('estado', 'Activo')
            )

            imagen = producto_encontrado.get('imagen_url')
            archivo_imagen = request.files.get('archivo_imagen')

            if (
                archivo_imagen
                and archivo_imagen.filename != ''
                and allowed_file(archivo_imagen.filename)
            ):
                nombre_seguro = secure_filename(archivo_imagen.filename)
                nombre_final = (
                    f'prod_{random.randint(10000, 99999)}_{nombre_seguro}'
                )
                ruta_guardado = os.path.join(
                    app.root_path, app.config['UPLOAD_FOLDER'], nombre_final
                )
                archivo_imagen.save(ruta_guardado)
                imagen = url_for(
                    'static', filename=f'uploads/productos/{nombre_final}'
                )
            elif (
                hasattr(form, 'imagen_url')
                and form.imagen_url.data
                and form.imagen_url.data.strip()
            ):
                imagen = form.imagen_url.data.strip()

            cursor.execute(
                """
                UPDATE productos 
                SET codigo_barras = %s, nombre = %s, precio = %s, costo = %s,
                    stock = %s, stock_minimo = %s, unidad_medida = %s,
                    imagen_url = %s, estado = %s
                WHERE id = %s
                """,
                (
                    codigo,
                    nombre,
                    precio,
                    costo,
                    stock,
                    stock_minimo,
                    unidad,
                    imagen,
                    nuevo_estado,
                    id,
                ),
            )

            conn.commit()
            flash('¡Producto actualizado con éxito!', 'success')
            return redirect(url_for('productos'))

        elif request.method == 'GET':
            form.nombre.data = producto_encontrado['nombre']
            form.precio.data = producto_encontrado['precio']
            form.stock.data = producto_encontrado['stock']
            if hasattr(form, 'costo'):
                form.costo.data = producto_encontrado.get('costo', 0.0)
            if hasattr(form, 'codigo_barras'):
                form.codigo_barras.data = producto_encontrado.get('codigo_barras', '')
            if hasattr(form, 'stock_minimo'):
                form.stock_minimo.data = producto_encontrado.get('stock_minimo', 3)
            if hasattr(form, 'unidad_medida'):
                form.unidad_medida.data = producto_encontrado.get(
                    'unidad_medida', 'Unidad'
                )
            if hasattr(form, 'imagen_url'):
                form.imagen_url.data = producto_encontrado.get('imagen_url') or ''

    except Exception as e:
        conn.rollback()
        flash(f'Error al actualizar producto: {e}', 'danger')
    finally:
        cursor.close()
        conn.close()

    return render_template(
        'formulario_producto.html',
        form=form,
        editando=True,
        producto=producto_encontrado,
    )


@app.route(
    '/productos/cambiar-estado/<int:id>/<string:nuevo_estado>',
    methods=['GET', 'POST'],
)
@login_required
@admin_required
def cambiar_estado_producto(id, nuevo_estado):
    if nuevo_estado not in ['Activo', 'Inactivo']:
        flash('Estado no válido.', 'danger')
        return redirect(url_for('productos'))

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'UPDATE productos SET estado = %s WHERE id = %s', (nuevo_estado, id)
        )
        conn.commit()
        msg = (
            'desactivado del catálogo'
            if nuevo_estado == 'Inactivo'
            else 'reactivado con éxito'
        )
        flash(f'El producto ha sido {msg}.', 'info')
    except Exception as e:
        conn.rollback()
        flash(f'Error al cambiar el estado: {e}', 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('productos'))


@app.route('/productos/borrar/<int:id>')
@login_required
@admin_required
def borrar_producto(id):
    return cambiar_estado_producto(id, 'Inactivo')


# -----------------------------------------------------------------------------
# 3. CONTROL DEL CARRITO EN SESIÓN
# -----------------------------------------------------------------------------
@app.route('/carrito/agregar/<int:producto_id>', methods=['POST'])
@login_required
def agregar_al_carrito(producto_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(
            "SELECT id, nombre, precio, stock, imagen_url FROM productos WHERE id = %s AND estado = 'Activo'",
            (producto_id,),
        )
        prod = cursor.fetchone()
        if not prod or prod['stock'] <= 0:
            flash('Producto no disponible en stock.', 'warning')
            return redirect(url_for('productos'))

        carrito = session.get('carrito', {})
        p_key = str(producto_id)
        cant_actual = carrito.get(p_key, {}).get('cantidad', 0)

        if cant_actual + 1 > prod['stock']:
            flash(
                f"Solo disponemos de {prod['stock']} unidades de {prod['nombre']}.",
                'warning',
            )
            return redirect(url_for('productos'))

        carrito[p_key] = {
            'id': prod['id'],
            'nombre': prod['nombre'],
            'precio': float(prod['precio']),
            'imagen_url': (
                prod['imagen_url']
                or 'https://images.unsplash.com/photo-1597854710119-a5a84396736a?w=400'
            ),
            'cantidad': cant_actual + 1,
        }
        session['carrito'] = carrito
        session.modified = True
        flash(f'¡{prod["nombre"]} agregado al carrito!', 'success')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('ver_carrito'))


@app.route('/carrito')
@login_required
def ver_carrito():
    carrito = session.get('carrito', {})
    subtotal = sum(item['precio'] * item['cantidad'] for item in carrito.values())
    iva = round(subtotal * 0.15, 2)
    total = round(subtotal + iva, 2)
    return render_template(
        'carrito.html',
        carrito=carrito,
        subtotal=subtotal,
        iva=iva,
        total=total,
    )


@app.route('/carrito/eliminar/<int:producto_id>', methods=['POST'])
@login_required
def eliminar_del_carrito(producto_id):
    carrito = session.get('carrito', {})
    p_key = str(producto_id)
    if p_key in carrito:
        del carrito[p_key]
        session['carrito'] = carrito
        session.modified = True
        flash('Producto retirado del carrito.', 'info')
    return redirect(url_for('ver_carrito'))


# -----------------------------------------------------------------------------
# 4. FINALIZAR COMPRA: SECUENCIAL PENDIENTE DINÁMICO (NO VIOLA UNIQUE EN SRI)
# -----------------------------------------------------------------------------
@app.route('/carrito/checkout', methods=['POST'])
@app.route('/carrito/pagar', methods=['POST'])
@app.route('/carrito/procesar', methods=['POST'])
@login_required
def checkout_factura():
    carrito = session.get('carrito', {})
    if not carrito:
        flash('El carrito está vacío.', 'warning')
        return redirect(url_for('productos'))

    usuario_id = session.get('usuario_id')
    metodo_pago = request.form.get('metodo_pago', 'Transferencia Bancaria')
    comprobante = request.form.get('comprobante', '').strip()

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(
            'SELECT id FROM clientes WHERE usuario_id = %s LIMIT 1', (usuario_id,)
        )
        cli = cursor.fetchone()
        if cli:
            cliente_id = cli['id']
        else:
            cursor.execute(
                "SELECT id FROM clientes WHERE cedula = '9999999999' LIMIT 1"
            )
            cf = cursor.fetchone()
            if cf:
                cliente_id = cf['id']
            else:
                cursor.execute(
                    """
                    INSERT INTO clientes (cedula, nombre, apellido, telefono, email, estado)
                    VALUES ('9999999999', 'Consumidor', 'Final', '0999999999', 'consumidorfinal@barberia.com', 'Activo')
                    RETURNING id
                    """
                )
                cliente_id = cursor.fetchone()['id']

        subtotal = 0.0
        for p_id, item in carrito.items():
            cursor.execute(
                'SELECT stock, precio FROM productos WHERE id = %s FOR UPDATE',
                (int(p_id),),
            )
            p_db = cursor.fetchone()
            if not p_db or p_db['stock'] < item['cantidad']:
                conn.rollback()
                flash(f"Stock insuficiente para {item['nombre']}.", 'danger')
                return redirect(url_for('ver_carrito'))
            subtotal += float(p_db['precio']) * item['cantidad']

        subtotal = round(subtotal, 2)
        iva = round(subtotal * 0.15, 2)
        total = round(subtotal + iva, 2)

        cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 AS siguiente_id FROM facturas")
        next_id = cursor.fetchone()['siguiente_id']
        nro_factura = f'PEND-{next_id:08d}'

        cursor.execute(
            """
            INSERT INTO facturas (
                num_factura,
                numero_factura,
                cliente_id, 
                usuario_id, 
                subtotal, 
                iva, 
                impuestos,
                descuento, 
                total, 
                metodo_pago, 
                comprobante_transferencia, 
                estado,
                fecha,
                activo
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, 0.00, %s, %s, %s, 'Pendiente', CURRENT_TIMESTAMP, TRUE)
            RETURNING id
            """,
            (
                nro_factura,
                nro_factura,
                cliente_id,
                usuario_id,
                subtotal,
                iva,
                iva,
                total,
                metodo_pago,
                comprobante,
            ),
        )
        factura_id = cursor.fetchone()['id']

        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'factura_detalles'
        """)
        cols_existentes = [r['column_name'] for r in cursor.fetchall()]

        for p_id, item in carrito.items():
            cant = int(item['cantidad'])
            precio = float(item['precio'])
            sub_item = round(cant * precio, 2)

            campos = ['factura_id', 'producto_id', 'cantidad']
            valores = [factura_id, int(p_id), cant]

            if 'precio_unitario' in cols_existentes:
                campos.append('precio_unitario')
                valores.append(precio)
            elif 'precio' in cols_existentes:
                campos.append('precio')
                valores.append(precio)

            if 'subtotal' in cols_existentes:
                campos.append('subtotal')
                valores.append(sub_item)
            if 'subtotal_linea' in cols_existentes:
                campos.append('subtotal_linea')
                valores.append(sub_item)
            if 'total' in cols_existentes:
                campos.append('total')
                valores.append(sub_item)

            placeholders = ', '.join(['%s'] * len(campos))
            cols_str = ', '.join(campos)
            query_detalle = f'INSERT INTO factura_detalles ({cols_str}) VALUES ({placeholders})'

            try:
                cursor.execute(query_detalle, tuple(valores))
            except Exception as e_det:
                print('Advertencia al insertar detalle:', e_det)

            cursor.execute(
                """
                UPDATE productos 
                SET stock = GREATEST(0, stock - %s) 
                WHERE id = %s
                """,
                (cant, int(p_id)),
            )

        conn.commit()
        session.pop('carrito', None)
        session.modified = True

        flash(
            '¡Pedido registrado exitosamente! Su compra se encuentra Pendiente de Confirmación por el Administrador.',
            'warning',
        )
        return redirect(url_for('facturacion'))

    except Exception as e:
        conn.rollback()
        print('ERROR CRÍTICO AL PROCESAR PEDIDO:', e)
        flash(f'Error al procesar el pedido: {e}', 'danger')
        return redirect(url_for('ver_carrito'))
    finally:
        cursor.close()
        conn.close()


# -----------------------------------------------------------------------------
# 5. GESTIÓN Y LISTADO GENERAL DE FACTURACIÓN (CON BUSCADOR CON LUPITA)
# -----------------------------------------------------------------------------
@app.route('/facturacion')
@login_required
def facturacion():
    rol = session.get('rol', 'Cliente')
    usuario_actual_id = session.get('usuario_id')
    busqueda = request.args.get('q', '').strip()

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        if rol == 'Administrador':
            query = """
                SELECT 
                    f.id,
                    COALESCE(f.numero_factura, f.num_factura, '#' || f.id::text) AS numero_factura,
                    COALESCE(f.numero_factura, f.num_factura, '#' || f.id::text) AS num_factura,
                    COALESCE(f.fecha, CURRENT_TIMESTAMP) AS fecha,
                    COALESCE(f.subtotal, 0.00) AS subtotal,
                    COALESCE(f.iva, f.impuestos, 0.00) AS iva,
                    COALESCE(f.total, 0.00) AS total,
                    COALESCE(f.estado, 'Pendiente') AS estado,
                    COALESCE(f.metodo_pago, 'Efectivo') AS metodo_pago,
                    COALESCE(
                        NULLIF(TRIM(c.nombre || ' ' || COALESCE(c.apellido, '')), ''),
                        u.nombre_completo,
                        'Consumidor Final'
                    ) AS cliente,
                    COALESCE(c.email, u.email, 'S/C') AS identificacion,
                    COALESCE(f.comprobante_transferencia, '') AS comprobante_transferencia,
                    COALESCE(f.activo, TRUE) AS activo
                FROM facturas f
                LEFT JOIN clientes c ON f.cliente_id = c.id
                LEFT JOIN usuarios u ON f.usuario_id = u.id
                WHERE f.estado != 'Inactivo'
            """
            params = []
            if busqueda:
                query += """ AND (
                    f.numero_factura ILIKE %s OR 
                    f.num_factura ILIKE %s OR 
                    c.nombre ILIKE %s OR 
                    c.apellido ILIKE %s OR 
                    u.nombre_completo ILIKE %s OR 
                    COALESCE(f.comprobante_transferencia, '') ILIKE %s
                )"""
                p_term = f"%{busqueda}%"
                params = [p_term, p_term, p_term, p_term, p_term, p_term]

            query += " ORDER BY f.id DESC"
            cursor.execute(query, tuple(params))
            facturas = cursor.fetchall()
            return render_template('facturacion.html', facturas=facturas, es_admin=True, busqueda=busqueda)
        else:
            query = """
                SELECT 
                    f.id,
                    COALESCE(f.numero_factura, f.num_factura, '#' || f.id::text) AS numero_factura,
                    COALESCE(f.numero_factura, f.num_factura, '#' || f.id::text) AS num_factura,
                    COALESCE(f.fecha, CURRENT_TIMESTAMP) AS fecha,
                    COALESCE(f.subtotal, 0.00) AS subtotal,
                    COALESCE(f.iva, f.impuestos, 0.00) AS iva,
                    COALESCE(f.total, 0.00) AS total,
                    COALESCE(f.estado, 'Pendiente') AS estado,
                    COALESCE(f.metodo_pago, 'Efectivo') AS metodo_pago,
                    COALESCE(
                        NULLIF(TRIM(c.nombre || ' ' || COALESCE(c.apellido, '')), ''),
                        u.nombre_completo,
                        'Cliente'
                    ) AS cliente,
                    COALESCE(c.email, u.email, 'S/C') AS identificacion,
                    COALESCE(f.comprobante_transferencia, '') AS comprobante_transferencia,
                    COALESCE(f.activo, TRUE) AS activo
                FROM facturas f
                LEFT JOIN clientes c ON f.cliente_id = c.id
                LEFT JOIN usuarios u ON f.usuario_id = u.id
                WHERE (f.usuario_id = %s OR c.usuario_id = %s)
                  AND f.estado != 'Inactivo'
            """
            params = [usuario_actual_id, usuario_actual_id]
            if busqueda:
                query += " AND (f.numero_factura ILIKE %s OR COALESCE(f.comprobante_transferencia, '') ILIKE %s)"
                params.extend([f"%{busqueda}%", f"%{busqueda}%"])

            query += " ORDER BY f.id DESC"
            cursor.execute(query, tuple(params))
            facturas = cursor.fetchall()
            return render_template('facturacion.html', facturas=facturas, es_admin=False, busqueda=busqueda)
    finally:
        cursor.close()
        conn.close()


# -----------------------------------------------------------------------------
# 6. CONFIRMAR PAGO (ADMINISTRADOR) Y EMISIÓN OFICIAL SRI (SIN BLOQUEO TRIGGER)
# -----------------------------------------------------------------------------
@app.route('/facturacion/confirmar-pago/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def confirmar_pago_factura(id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("SELECT * FROM facturas WHERE id = %s", (id,))
        fac = cursor.fetchone()
        if not fac:
            flash('La orden especificada no existe.', 'warning')
            return redirect(url_for('facturacion'))

        # Secuencial oficial SRI tipo 001-001-XXXXXXXXX
        cursor.execute("""
            SELECT COALESCE(MAX(id), 0) + 1 AS siguiente_id 
            FROM facturas 
            WHERE numero_factura NOT LIKE 'PEND-%' 
              AND num_factura NOT LIKE 'PEND-%'
        """)
        next_id = cursor.fetchone()['siguiente_id']
        numero_factura = f'001-001-{next_id:09d}'

        try:
            cursor.execute("""
                UPDATE facturas 
                SET estado = 'Pagada', numero_factura = %s, num_factura = %s, fecha = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (numero_factura, numero_factura, id))
            conn.commit()
            flash(f'¡Pago verificado y aceptado! Factura oficial Nº {numero_factura} emitida.', 'success')
        except psycopg2.Error:
            conn.rollback()
            cursor.execute("UPDATE facturas SET estado = 'Pagada' WHERE id = %s", (id,))
            conn.commit()
            flash(f'¡Pago confirmado! Comprobante #{id} marcado como Pagado y listo para imprimir.', 'success')

    except Exception as e:
        conn.rollback()
        flash(f'Error al confirmar el pago: {e}', 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('facturacion'))


# -----------------------------------------------------------------------------
# 7. CONFIRMAR PAGO DE CITA Y EMISIÓN DE FACTURA LEGAL AUTOMÁTICA
# -----------------------------------------------------------------------------
@app.route('/citas/confirmar-pago/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def confirmar_pago_cita(id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("""
            SELECT c.*, cl.usuario_id AS cli_usuario_id, cl.nombre, cl.apellido
            FROM citas c
            LEFT JOIN clientes cl ON c.cliente_id = cl.id
            WHERE c.id = %s
        """, (id,))
        cita = cursor.fetchone()

        if not cita:
            flash('La cita solicitada no existe.', 'warning')
            return redirect(url_for('citas'))

        precios_servicios = {
            'Corte de Cabello': 7.00,
            'Arreglo de Barba Clásica': 5.00,
            'Cuidado y Limpieza Facial': 8.00,
            'Combo Completo (Corte + Barba + Facial)': 18.00,
        }
        subtotal = float(precios_servicios.get(cita['servicio'], 10.00))
        iva = round(subtotal * 0.15, 2)
        total = round(subtotal + iva, 2)

        cursor.execute("""
            SELECT COALESCE(MAX(id), 0) + 1 AS siguiente_id 
            FROM facturas 
            WHERE numero_factura NOT LIKE 'PEND-%'
        """)
        next_id = cursor.fetchone()['siguiente_id']
        nro_oficial = f'001-001-{next_id:09d}'

        cursor.execute("""
            INSERT INTO facturas (
                num_factura, numero_factura, cliente_id, usuario_id,
                subtotal, iva, impuestos, descuento, total,
                metodo_pago, comprobante_transferencia, estado, fecha, activo
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, 0.00, %s, %s, %s, 'Pagada', CURRENT_TIMESTAMP, TRUE)
            RETURNING id
        """, (
            nro_oficial, nro_oficial, cita['cliente_id'], cita.get('cli_usuario_id'),
            subtotal, iva, iva, total,
            cita.get('metodo_pago', 'Efectivo en Barbería'),
            cita.get('comprobante_pago', '')
        ))
        nueva_factura_id = cursor.fetchone()['id']

        cursor.execute("UPDATE citas SET estado = 'Pagada' WHERE id = %s", (id,))
        conn.commit()

        flash(f'¡Pago de Cita #{id} confirmado! Factura oficial Nº {nro_oficial} emitida.', 'success')
        return redirect(url_for('ver_factura', id=nueva_factura_id) + '?print=true')

    except Exception as e:
        conn.rollback()
        flash(f'Error al confirmar pago de cita: {e}', 'danger')
        return redirect(url_for('citas'))
    finally:
        cursor.close()
        conn.close()


# -----------------------------------------------------------------------------
# 8. FACTURAR Y COBRAR DIRECTAMENTE UNA CITA (DESDE EL BOTÓN COBRAR)
# -----------------------------------------------------------------------------
@app.route('/citas/cobrar/<int:cita_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def cobrar_cita(cita_id):
    return confirmar_pago_cita(cita_id)


# -----------------------------------------------------------------------------
# 9. EDITAR FACTURA (FORMULARIO CONECTADO A POSTGRESQL)
# -----------------------------------------------------------------------------
@app.route('/facturacion/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_factura(id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(
            """
            SELECT f.*, 
                   COALESCE(NULLIF(TRIM(c.nombre || ' ' || COALESCE(c.apellido, '')), ''), u.nombre_completo, 'Consumidor Final') AS cliente_nombre
            FROM facturas f
            LEFT JOIN clientes c ON f.cliente_id = c.id
            LEFT JOIN usuarios u ON f.usuario_id = u.id
            WHERE f.id = %s
            """,
            (id,),
        )
        factura = cursor.fetchone()

        if not factura:
            flash('La factura especificada no existe.', 'warning')
            return redirect(url_for('facturacion'))

        form = FacturaForm()

        if request.method == 'POST':
            try:
                nuevo_estado = request.form.get('estado', factura.get('estado', 'Pagada'))
                nuevo_metodo = request.form.get('metodo_pago', factura.get('metodo_pago', 'Efectivo'))
                subtotal = float(request.form.get('subtotal') or factura.get('subtotal') or 0.0)
                descuento = float(request.form.get('descuento') or factura.get('descuento') or 0.0)
                iva = float(request.form.get('impuestos') or request.form.get('iva') or factura.get('iva') or 0.0)
                total = float(request.form.get('total') or (subtotal - descuento + iva))

                nuevo_num_factura = factura.get('numero_factura')
                if factura.get('estado') == 'Pendiente' and nuevo_estado == 'Pagada':
                    cursor.execute(
                        "SELECT COALESCE(MAX(id), 0) + 1 AS siguiente_id FROM facturas WHERE numero_factura NOT LIKE 'PEND-%'"
                    )
                    next_id = cursor.fetchone()['siguiente_id']
                    nuevo_num_factura = f'001-001-{next_id:09d}'

                cliente_id_input = request.form.get('cliente_id')
                cliente_id = int(cliente_id_input) if (cliente_id_input and str(cliente_id_input).isdigit()) else factura.get('cliente_id')

                cursor.execute(
                    """
                    UPDATE facturas 
                    SET metodo_pago = %s, estado = %s, numero_factura = %s, num_factura = %s,
                        subtotal = %s, iva = %s, impuestos = %s, descuento = %s, total = %s,
                        cliente_id = %s
                    WHERE id = %s
                    """,
                    (
                        nuevo_metodo,
                        nuevo_estado,
                        nuevo_num_factura,
                        nuevo_num_factura,
                        subtotal,
                        iva,
                        iva,
                        descuento,
                        total,
                        cliente_id,
                        id,
                    ),
                )
                conn.commit()
                flash(f'Registro #{id} actualizado exitosamente.', 'success')
                return redirect(url_for('facturacion'))
            except Exception as e_post:
                conn.rollback()
                flash(f'Error al actualizar la factura: {e_post}', 'danger')

        cursor.execute("SELECT id, nombre, precio, stock FROM productos WHERE estado = 'Activo' ORDER BY nombre ASC")
        productos_lista = cursor.fetchall()

        cursor.execute("SELECT id, nombre, precio FROM servicios WHERE estado = 'Activo' ORDER BY nombre ASC")
        servicios_lista = cursor.fetchall()

        cursor.execute("""
            SELECT id, COALESCE(NULLIF(TRIM(nombre || ' ' || COALESCE(apellido, '')), ''), nombre, 'Cliente') AS nombre, 
                   COALESCE(cedula, '9999999999') AS cedula
            FROM clientes
            WHERE estado = 'Activo'
            ORDER BY nombre ASC
        """)
        clientes_lista = cursor.fetchall()

        cursor.execute("SELECT ruc, empresa FROM proveedores WHERE estado = 'Activo' ORDER BY empresa ASC")
        proveedores_lista = cursor.fetchall()

        return render_template(
            'formulario_facturacion.html',
            form=form,
            editando=True,
            factura=factura,
            productos=productos_lista,
            servicios=servicios_lista,
            clientes=clientes_lista,
            proveedores=proveedores_lista,
        )
    finally:
        cursor.close()
        conn.close()


@app.route('/facturacion/eliminar/<int:id>', methods=['POST', 'GET'])
@login_required
@admin_required
def eliminar_factura(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE facturas 
            SET activo = FALSE, estado = 'Inactivo' 
            WHERE id = %s
            """,
            (id,),
        )
        conn.commit()
        flash(f'Factura #{id} dada de baja del sistema (marcada como Inactiva).', 'warning')
    except Exception as e:
        conn.rollback()
        flash(f'Error al procesar la factura: {e}', 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('facturacion'))


@app.route('/facturacion/nueva', methods=['GET', 'POST'])
@login_required
@admin_required
def nueva_factura():
    form = FacturaForm()
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        if request.method == 'POST':
            subtotal = float(request.form.get('subtotal') or 0.0)
            descuento = float(request.form.get('descuento') or 0.0)
            iva = float(request.form.get('impuestos') or request.form.get('iva') or 0.0)
            total = float(request.form.get('total') or (subtotal - descuento + iva))

            metodo_pago = request.form.get('metodo_pago', 'Efectivo')
            estado = request.form.get('estado', 'Pagada')

            cliente_id_input = request.form.get('cliente_id')
            cliente_id = None
            if cliente_id_input and str(cliente_id_input).strip() not in ['', '0', 'None']:
                cliente_id = int(cliente_id_input)

            if not cliente_id:
                cursor.execute(
                    'SELECT id FROM clientes WHERE cedula = %s OR nombre ILIKE %s LIMIT 1',
                    ('9999999999', '%Consumidor Final%'),
                )
                cf = cursor.fetchone()
                if cf:
                    cliente_id = cf['id']
                else:
                    cursor.execute(
                        """
                        INSERT INTO clientes (cedula, nombre, apellido, telefono, email, estado)
                        VALUES ('9999999999', 'Consumidor', 'Final', '0999999999', 'consumidorfinal@barberia.com', 'Activo')
                        RETURNING id
                        """
                    )
                    cliente_id = cursor.fetchone()['id']

            if estado == 'Pendiente':
                cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 AS siguiente_id FROM facturas")
                next_id = cursor.fetchone()['siguiente_id']
                numero_factura = f'PEND-{next_id:08d}'
            else:
                cursor.execute(
                    "SELECT COALESCE(MAX(id), 0) + 1 AS siguiente_id FROM facturas WHERE numero_factura NOT LIKE 'PEND-%'"
                )
                next_id = cursor.fetchone()['siguiente_id']
                numero_factura = f'001-001-{next_id:09d}'

            cursor.execute(
                """
                INSERT INTO facturas (
                    num_factura,
                    numero_factura, 
                    fecha, 
                    subtotal, 
                    iva, 
                    impuestos, 
                    descuento, 
                    total, 
                    estado, 
                    cliente_id, 
                    usuario_id, 
                    metodo_pago,
                    activo
                ) VALUES (%s, %s, CURRENT_TIMESTAMP, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
                RETURNING id
                """,
                (
                    numero_factura,
                    numero_factura,
                    subtotal,
                    iva,
                    iva,
                    descuento,
                    total,
                    estado,
                    cliente_id,
                    session.get('usuario_id'),
                    metodo_pago,
                ),
            )
            nueva_factura_id = cursor.fetchone()['id']
            conn.commit()

            if estado == 'Pendiente':
                flash(f'Registro guardado como Pendiente de Pago (ID #{nueva_factura_id}).', 'warning')
                return redirect(url_for('facturacion'))

            flash(f'Factura Nº {numero_factura} emitida con éxito.', 'success')
            return redirect(url_for('ver_factura', id=nueva_factura_id))

        cursor.execute("SELECT id, nombre, precio, stock FROM productos WHERE estado = 'Activo' ORDER BY nombre ASC")
        productos_lista = cursor.fetchall()

        cursor.execute("SELECT id, nombre, precio FROM servicios WHERE estado = 'Activo' ORDER BY nombre ASC")
        servicios_lista = cursor.fetchall()

        cursor.execute("""
            SELECT id, COALESCE(NULLIF(TRIM(nombre || ' ' || COALESCE(apellido, '')), ''), nombre, 'Cliente') AS nombre, 
                   COALESCE(cedula, '9999999999') AS cedula
            FROM clientes
            WHERE estado = 'Activo'
            ORDER BY nombre ASC
        """)
        clientes_lista = cursor.fetchall()

        cursor.execute("SELECT ruc, empresa FROM proveedores WHERE estado = 'Activo' ORDER BY empresa ASC")
        proveedores_lista = cursor.fetchall()

        return render_template(
            'formulario_facturacion.html',
            form=form,
            editando=False,
            productos=productos_lista,
            servicios=servicios_lista,
            clientes=clientes_lista,
            proveedores=proveedores_lista,
        )

    except Exception as e:
        conn.rollback()
        flash(f'Ocurrió un error al registrar la factura: {str(e)}', 'danger')
        return redirect(url_for('facturacion'))

    finally:
        cursor.close()
        conn.close()


# -----------------------------------------------------------------------------
# 10. DETALLE, VISUALIZACIÓN E IMPRESIÓN DIRECTA EN FORMATO PDF
# -----------------------------------------------------------------------------
@app.route('/factura/<int:id>')
@app.route('/facturacion/detalle/<int:id>')
@login_required
def ver_factura(id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(
            """
            SELECT 
                f.*,
                COALESCE(f.numero_factura, f.num_factura, '001-001-' || LPAD(f.id::text, 9, '0')) AS numero_factura,
                COALESCE(
                    NULLIF(TRIM(c.nombre || ' ' || COALESCE(c.apellido, '')), ''),
                    u.nombre_completo,
                    'Consumidor Final'
                ) AS cliente_nombre,
                COALESCE(c.cedula, '9999999999999') AS cliente_identificacion,
                COALESCE(c.telefono, 'S/N') AS cliente_telefono,
                COALESCE(c.email, u.email, 'cliente@barberiahernandez.com') AS cliente_email,
                'Puembo, Pichincha, Ecuador' AS cliente_direccion
            FROM facturas f
            LEFT JOIN clientes c ON f.cliente_id = c.id
            LEFT JOIN usuarios u ON f.usuario_id = u.id
            WHERE f.id = %s
            """,
            (id,),
        )
        factura = cursor.fetchone()

        if not factura:
            flash('No se encontró el comprobante solicitado.', 'warning')
            return redirect(url_for('facturacion'))

        cursor.execute(
            """
            SELECT 
                fd.*,
                COALESCE(p.nombre, 'Servicio Profesional de Barbería') AS item_nombre,
                COALESCE(p.codigo_barras, 'SRV-' || LPAD(COALESCE(fd.producto_id, 1)::text, 4, '0')) AS codigo,
                COALESCE(fd.subtotal, fd.subtotal_linea, fd.total, (fd.cantidad * fd.precio_unitario)) AS subtotal
            FROM factura_detalles fd
            LEFT JOIN productos p ON fd.producto_id = p.id
            WHERE fd.factura_id = %s
            ORDER BY fd.id ASC
            """,
            (factura['id'],),
        )
        detalles = cursor.fetchall()

        if not detalles:
            detalles = [{
                'codigo': 'SERV-001',
                'item_nombre': 'Atención y Servicio Profesional de Barbería',
                'cantidad': 1,
                'precio_unitario': factura['subtotal'],
                'subtotal': factura['subtotal']
            }]

        es_admin = session.get('rol') == 'Administrador'
        imprimir_auto = request.args.get('print') == 'true'

        return render_template(
            'detalle_factura.html',
            factura=factura,
            detalles=detalles,
            es_admin=es_admin,
            imprimir_auto=imprimir_auto,
        )

    except Exception as e:
        conn.rollback()
        flash(f'Error al cargar la factura: {e}', 'danger')
        return redirect(url_for('facturacion'))
    finally:
        cursor.close()
        conn.close()


# =============================================================================
# 11. MÓDULO DE PROVEEDORES (PostgreSQL)
# =============================================================================
@app.route('/proveedores')
@login_required
@admin_required
def proveedores():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT * FROM proveedores ORDER BY ruc ASC')
    proveedores_db = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('proveedores.html', proveedores=proveedores_db)


@app.route('/proveedores/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def formulario_proveedor():
    form = ProveedorForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO proveedores (ruc, empresa, telefono, email, direccion, ciudad, nombre_contacto, telefono_contacto, dias_credito)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    form.ruc.data,
                    form.empresa.data,
                    form.telefono.data,
                    form.email.data,
                    form.direccion.data,
                    form.ciudad.data,
                    form.nombre_contacto.data,
                    form.telefono_contacto.data,
                    form.dias_credito.data,
                ),
            )
            conn.commit()
            flash('¡Proveedor registrado con éxito!', 'success')
        except psycopg2.IntegrityError:
            conn.rollback()
            flash('El RUC ingresado ya existe en la base de datos.', 'danger')
        except Exception as e:
            conn.rollback()
            flash(f'Error al registrar: {e}', 'danger')
        cursor.close()
        conn.close()
        return redirect(url_for('proveedores'))

    return render_template(
        'formulario_proveedores.html', form=form, editando=False
    )


@app.route('/proveedores/editar/<string:ruc>', methods=['GET', 'POST'])
@login_required
@admin_required
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
        cursor.execute(
            """
            UPDATE proveedores 
            SET empresa = %s, telefono = %s, email = %s, direccion = %s, 
                ciudad = %s, nombre_contacto = %s, telefono_contacto = %s, dias_credito = %s
            WHERE ruc = %s
            """,
            (
                form.empresa.data,
                form.telefono.data,
                form.email.data,
                form.direccion.data,
                form.ciudad.data,
                form.nombre_contacto.data,
                form.telefono_contacto.data,
                form.dias_credito.data,
                ruc,
            ),
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash('¡Proveedor actualizado con éxito!', 'success')
        return redirect(url_for('proveedores'))

    elif request.method == 'GET':
        form.ruc.data = proveedor_encontrado['ruc']
        form.empresa.data = proveedor_encontrado['empresa']
        form.telefono.data = proveedor_encontrado['telefono']
        form.email.data = proveedor_encontrado['email']
        form.direccion.data = proveedor_encontrado['direccion']
        form.ciudad.data = proveedor_encontrado['ciudad']
        form.nombre_contacto.data = proveedor_encontrado['nombre_contacto']
        form.telefono_contacto.data = proveedor_encontrado['telefono_contacto']
        form.dias_credito.data = proveedor_encontrado['dias_credito']

    cursor.close()
    conn.close()
    return render_template(
        'formulario_proveedores.html', form=form, editando=True
    )


@app.route('/proveedores/eliminar/<string:ruc>')
@login_required
@admin_required
def eliminar_proveedor(ruc):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM proveedores WHERE ruc = %s', (ruc,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('¡Proveedor eliminado con éxito!', 'warning')
    return redirect(url_for('proveedores'))


@app.route('/proveedores/cambiar/<string:ruc>')
@login_required
@admin_required
def cambiar_estado_proveedor(ruc):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE proveedores SET estado = CASE WHEN estado = 'Activo' THEN"
        " 'Inactivo' ELSE 'Activo' END WHERE ruc = %s",
        (ruc,),
    )
    conn.commit()
    cursor.close()
    conn.close()
    flash('¡Estado del proveedor actualizado con éxito!', 'success')
    return redirect(url_for('proveedores'))


# =============================================================================
# 12. MÓDULO DE CITAS (PostgreSQL CON BUSCADOR Y 3 MÉTODOS DE PAGO)
# =============================================================================
@app.route('/citas')
@login_required
def citas():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    rol_actual = session.get('rol')
    usuario_id = session.get('usuario_id')
    busqueda = request.args.get('q', '').strip()

    try:
        consulta_base = """
            SELECT c.id, c.barbero_id, c.servicio, c.fecha, c.hora, c.estado, c.cliente_id,
                   c.notas_cliente, c.motivo_cancelacion,
                   COALESCE(c.metodo_pago, 'Efectivo en Barbería') AS metodo_pago,
                   COALESCE(c.comprobante_pago, '') AS comprobante_pago,
                   COALESCE(
                       NULLIF(TRIM(cl.nombre || ' ' || cl.apellido), ''),
                       u.nombre_completo,
                       cl.nombre,
                       'Cliente General'
                   ) AS nombre_final,
                   COALESCE(cl.telefono, 'S/N') AS cliente_telefono
            FROM citas c
            LEFT JOIN clientes cl ON c.cliente_id = cl.id
            LEFT JOIN usuarios u ON cl.usuario_id = u.id
        """

        params = []
        if rol_actual == 'Administrador':
            if busqueda:
                consulta_base += """ WHERE (
                    cl.nombre ILIKE %s OR 
                    cl.apellido ILIKE %s OR 
                    u.nombre_completo ILIKE %s OR 
                    c.servicio ILIKE %s OR 
                    COALESCE(cl.telefono, '') ILIKE %s OR
                    COALESCE(c.comprobante_pago, '') ILIKE %s
                )"""
                p = f"%{busqueda}%"
                params = [p, p, p, p, p, p]
            consulta_base += ' ORDER BY c.id DESC'
        else:
            consulta_base += """
                WHERE (cl.usuario_id = %s OR c.cliente_id IN (
                    SELECT id FROM clientes WHERE usuario_id = %s
                ))
            """
            params = [usuario_id, usuario_id]
            if busqueda:
                consulta_base += " AND (c.servicio ILIKE %s OR COALESCE(c.comprobante_pago, '') ILIKE %s)"
                params.extend([f"%{busqueda}%", f"%{busqueda}%"])
            consulta_base += ' ORDER BY c.id DESC'

        cursor.execute(consulta_base, tuple(params))
        filas = cursor.fetchall()

        citas_db = []
        for fila in filas:
            b_id = fila.get('barbero_id')
            fila['barbero'] = BARBEROS_MAP.get(
                b_id, BARBEROS_MAP.get(str(b_id), 'Andrés Hernández')
            )
            nom = fila.get('nombre_final') or 'Cliente General'
            fila['cliente'] = nom
            fila['cliente_nombre'] = nom
            fila['nombre'] = nom
            fila['nombre_cliente'] = nom
            citas_db.append(fila)

    except Exception as e:
        flash(f'Error al cargar el listado de citas: {e}', 'danger')
        citas_db = []
    finally:
        cursor.close()
        conn.close()

    return render_template('citas.html', citas=citas_db, busqueda=busqueda)


@app.route('/citas/nueva', methods=['GET', 'POST'])
@login_required
def formulario_cita():
    form = CitaForm()
    usuario_id = session.get('usuario_id')
    rol_actual = session.get('rol')

    if request.method == 'GET':
        if hasattr(form, 'cliente') and not form.cliente.data:
            form.cliente.data = session.get('usuario_nombre', '')
        if hasattr(form, 'telefono') and not form.telefono.data:
            conn = get_db_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            try:
                cur.execute(
                    'SELECT telefono FROM clientes WHERE usuario_id = %s LIMIT 1',
                    (usuario_id,),
                )
                cl = cur.fetchone()
                if cl and cl.get('telefono'):
                    form.telefono.data = cl['telefono']
            except Exception:
                pass
            finally:
                cur.close()
                conn.close()

    if form.validate_on_submit():
        hora_seleccionada = form.hora.data
        if isinstance(hora_seleccionada, str):
            hora_seleccionada = dt.strptime(hora_seleccionada.strip(), '%H:%M').time()

        hora_inicio = time(9, 0)
        hora_fin = time(21, 0)

        if hora_seleccionada < hora_inicio or hora_seleccionada > hora_fin:
            flash(
                'El horario de atención es exclusivamente de 09:00 AM a 09:00 PM.',
                'warning',
            )
            return render_template('formulario_cita.html', form=form, editando=False)

        # Capturar la opción de pago (3 opciones)
        metodo_pago = request.form.get('metodo_pago', 'Efectivo en Barbería')
        comprobante = request.form.get('comprobante_pago', '').strip()

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            nombre_input = (
                form.cliente.data.strip()
                if (hasattr(form, 'cliente') and form.cliente.data)
                else session.get('usuario_nombre', 'Cliente General')
            )
            telefono_input = (
                form.telefono.data.strip()
                if (hasattr(form, 'telefono') and form.telefono.data)
                else '0999999999'
            )

            partes = nombre_input.split(' ', 1)
            nom = partes[0]
            ape = partes[1] if len(partes) > 1 else 'General'

            cursor.execute(
                """
                SELECT id FROM clientes 
                WHERE (usuario_id = %s AND %s != 'Administrador') OR telefono = %s
                LIMIT 1
                """,
                (usuario_id, rol_actual, telefono_input),
            )
            cliente_existente = cursor.fetchone()

            if cliente_existente:
                cliente_id = cliente_existente['id']
            else:
                cursor.execute(
                    """
                    INSERT INTO clientes (usuario_id, nombre, apellido, telefono)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        usuario_id if rol_actual == 'Cliente' else None,
                        nom,
                        ape,
                        telefono_input,
                    ),
                )
                cliente_id = cursor.fetchone()['id']

            b_val = form.barbero.data if hasattr(form, 'barbero') else '1'
            barbero_id_sql = int(b_val) if str(b_val).isdigit() else 1

            s_val = (
                form.servicio.data
                if hasattr(form, 'servicio')
                else 'Corte de Cabello'
            )
            servicio_nombre = SERVICIOS_MAP.get(s_val, s_val)

            notas_cli = None
            if hasattr(form, 'notas_cliente') and form.notas_cliente.data:
                notas_cli = form.notas_cliente.data.strip()
            elif request.form.get('notas_cliente'):
                notas_cli = request.form.get('notas_cliente').strip()

            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'citas'
            """)
            columnas_citas = [c['column_name'] for c in cursor.fetchall()]

            campos = ['cliente_id', 'barbero_id', 'servicio', 'fecha', 'hora', 'estado', 'notas_cliente']
            valores = [cliente_id, barbero_id_sql, servicio_nombre, form.fecha.data, form.hora.data, 'Pendiente', notas_cli]

            if 'metodo_pago' in columnas_citas:
                campos.append('metodo_pago')
                valores.append(metodo_pago)
            if 'comprobante_pago' in columnas_citas:
                campos.append('comprobante_pago')
                valores.append(comprobante)

            placeholders = ', '.join(['%s'] * len(campos))
            cols_str = ', '.join(campos)
            query_insert = f"INSERT INTO citas ({cols_str}) VALUES ({placeholders})"

            cursor.execute(query_insert, tuple(valores))
            conn.commit()

            flash('¡Cita agendada exitosamente! El pago queda pendiente de verificación por administración.', 'info')
            return redirect(url_for('citas'))

        except Exception as e:
            conn.rollback()
            print('Error SQL al guardar cita:', e)
            flash(f'Error al registrar la cita: {e}', 'danger')
        finally:
            cursor.close()
            conn.close()

    return render_template('formulario_cita.html', form=form, editando=False)


@app.route('/citas/cambiar/<int:id>')
@login_required
def cambiar_estado_cita(id):
    if session.get('rol') != 'Administrador':
        flash(
            'Acceso restringido: solo el Administrador puede modificar el estado de una cita.',
            'danger',
        )
        return redirect(url_for('citas'))

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute('SELECT estado FROM citas WHERE id = %s', (id,))
        cita = cursor.fetchone()

        if not cita:
            flash('La cita solicitada no existe.', 'warning')
            return redirect(url_for('citas'))

        estado_actual = cita['estado']
        if estado_actual == 'Pendiente':
            nuevo_estado = 'Confirmada'
        elif estado_actual == 'Confirmada':
            nuevo_estado = 'Pagada'
        else:
            nuevo_estado = 'Pendiente'

        cursor.execute(
            'UPDATE citas SET estado = %s WHERE id = %s', (nuevo_estado, id)
        )
        conn.commit()
        flash(
            f'¡Estado de la cita #{id} actualizado a "{nuevo_estado}"!', 'success'
        )
    except Exception as e:
        conn.rollback()
        flash(f'Error al cambiar estado: {e}', 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('citas'))


@app.route('/citas/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_cita(id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    rol_actual = session.get('rol')
    usuario_id = session.get('usuario_id')

    cursor.execute(
        """
        SELECT c.*, 
               COALESCE(NULLIF(TRIM(cl.nombre || ' ' || cl.apellido), ''), u.nombre_completo, 'Cliente General') AS cliente_nombre,
               COALESCE(cl.telefono, 'S/N') AS cliente_telefono,
               cl.usuario_id AS cliente_usuario_id
        FROM citas c
        LEFT JOIN clientes cl ON c.cliente_id = cl.id
        LEFT JOIN usuarios u ON cl.usuario_id = u.id
        WHERE c.id = %s
        """,
        (id,),
    )
    cita = cursor.fetchone()

    if not cita:
        cursor.close()
        conn.close()
        flash('La cita solicitada no existe.', 'warning')
        return redirect(url_for('citas'))

    if rol_actual != 'Administrador' and cita['cliente_usuario_id'] != usuario_id:
        cursor.close()
        conn.close()
        flash('No cuenta con permisos para modificar esta cita.', 'danger')
        return redirect(url_for('citas'))

    form = CitaForm()

    if request.method == 'GET':
        if hasattr(form, 'cliente'):
            form.cliente.data = cita['cliente_nombre']
        if hasattr(form, 'telefono'):
            form.telefono.data = cita['cliente_telefono']
        if hasattr(form, 'fecha'):
            form.fecha.data = cita['fecha']
        if hasattr(form, 'hora'):
            form.hora.data = cita['hora']
        if hasattr(form, 'barbero'):
            form.barbero.data = str(cita['barbero_id'])
        if hasattr(form, 'servicio'):
            servicio_actual = cita['servicio']
            codigo_servicio = '1'
            for k, v in SERVICIOS_MAP.items():
                if v == servicio_actual and str(k).isdigit():
                    codigo_servicio = str(k)
                    break
            form.servicio.data = codigo_servicio

    if form.validate_on_submit():
        hora_seleccionada = form.hora.data
        if isinstance(hora_seleccionada, str):
            hora_seleccionada = dt.strptime(hora_seleccionada.strip(), '%H:%M').time()

        if hora_seleccionada < time(9, 0) or hora_seleccionada > time(21, 0):
            flash(
                'El horario de atención es exclusivamente de 09:00 AM a 09:00 PM.',
                'warning',
            )
            return render_template(
                'formulario_cita.html', form=form, editando=True, cita_id=id
            )

        try:
            b_val = form.barbero.data if hasattr(form, 'barbero') else '1'
            barbero_id_sql = int(b_val) if str(b_val).isdigit() else 1

            s_val = (
                form.servicio.data
                if hasattr(form, 'servicio')
                else 'Corte de Cabello'
            )
            servicio_nombre = SERVICIOS_MAP.get(s_val, s_val)

            cursor.execute(
                """
                UPDATE citas 
                SET barbero_id = %s, servicio = %s, fecha = %s, hora = %s
                WHERE id = %s
                """,
                (
                    barbero_id_sql,
                    servicio_nombre,
                    form.fecha.data,
                    form.hora.data,
                    id,
                ),
            )

            conn.commit()
            flash(f'¡Cita #{id} modificada y guardada con éxito!', 'success')
            return redirect(url_for('citas'))
        except Exception as e:
            conn.rollback()
            print('Error SQL al editar cita:', e)
            flash(f'Error al actualizar la cita: {e}', 'danger')
        finally:
            cursor.close()
            conn.close()
    else:
        cursor.close()
        conn.close()

    return render_template(
        'formulario_cita.html', form=form, editando=True, cita_id=id
    )


@app.route('/citas/eliminar/<int:id>', methods=['GET', 'POST'])
@login_required
def eliminar_cita(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        motivo = request.form.get('motivo_cancelacion')
        if motivo:
            cursor.execute(
                """
                UPDATE citas 
                SET estado = 'Cancelada', motivo_cancelacion = %s 
                WHERE id = %s
                """,
                (motivo, id),
            )
            conn.commit()
            flash(f'¡Cita #{id} cancelada con motivo registrado!', 'warning')
        else:
            cursor.execute('DELETE FROM citas WHERE id = %s', (id,))
            conn.commit()
            flash('¡Cita eliminada con éxito!', 'warning')
    except Exception as e:
        conn.rollback()
        flash(f'Error al procesar la cita: {e}', 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('citas'))


if __name__ == '__main__':
    app.run(debug=True)