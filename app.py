from flask import Flask, render_template, url_for

app = Flask(__name__)

# Ruta principal (Permite acceder con '/' o '/index')
@app.route('/')
@app.route('/index')
def home():
    return render_template('index.html')

# Ruta para el nuevo index1.html
@app.route('/index1')
def index1():
    return render_template('index1.html')

# Módulo de Productos
@app.route('/productos')
def productos():
    datos_productos = [
        {"id": "P001", "nombre": "Cera Capilar Mate", "categoria": "Styling", "precio": "$12.00"},
        {"id": "P002", "nombre": "Aceite Hidratante para Barba", "categoria": "Cuidado Facial", "precio": "$15.50"},
        {"id": "P003", "nombre": "Shampoo Anticaspa Pro", "categoria": "Aseo", "precio": "$9.00"}
    ]
    return render_template('productos.html', productos=datos_productos)

# Módulo de Clientes
@app.route('/clientes')
def clientes():
    datos_clientes = [
        {"id": 1, "nombre": "Carlos Mendoza", "telefono": "0998765432", "email": "carlos@example.com"},
        {"id": 2, "nombre": "Andrés Silva", "telefono": "0981234567", "email": "andres@example.com"}
    ]
    return render_template('clientes.html', clientes=datos_clientes)

# Módulo de Proveedores
@app.route('/proveedores')
def proveedores():
    datos_proveedores = [
        {"ruc": "1790011223001", "empresa": "Distribuidora BarberXP", "telefono": "022345678"},
        {"ruc": "1790044556001", "empresa": "Cosméticos Style Ecuador", "telefono": "022987654"}
    ]
    return render_template('proveedores.html', proveedores=datos_proveedores)

# Módulo de Facturación
@app.route('/facturacion')
def facturacion():
    datos_facturas = [
        {"num": "FAC-001", "cliente": "Carlos Mendoza", "monto": "$27.50", "estado": "Pagado"},
        {"num": "FAC-002", "cliente": "Andrés Silva", "monto": "$15.50", "estado": "Pendiente"}
    ]
    return render_template('facturacion.html', facturas=datos_facturas)

# Módulo de Citas Agendadas
@app.route('/citas')
def citas():
    datos_citas = [
        {"id": "C-001", "cliente": "Carlos Mendoza", "barbero": "Andres Hernández", "servicio": "Corte de Cabello + Barba", "fecha": "2026-08-15", "hora": "10:00 AM", "estado": "Confirmada"},
        {"id": "C-002", "cliente": "Andrés Silva", "barbero": "Mateo Romero", "servicio": "Perfilado de Barba", "fecha": "2026-08-15", "hora": "11:30 AM", "estado": "Pendiente"},
        {"id": "C-003", "cliente": "Juan Pérez", "barbero": "Ariel Hernández", "servicio": "Tinte y Limpieza Facial", "fecha": "2026-08-16", "hora": "03:00 PM", "estado": "Confirmada"}
    ]
    return render_template('citas.html', citas=datos_citas)

if __name__ == '__main__':
    app.run(debug=True)