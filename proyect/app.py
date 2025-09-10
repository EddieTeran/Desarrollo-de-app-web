from flask import Flask, render_template, redirect, url_for, flash, request
from datetime import datetime
import json
import csv
import os
from models import db, Producto
from forms import ProductoForm
from inventory import Inventario

# Inicializamos la aplicación Flask
app = Flask(__name__)

# Configuración de base de datos y seguridad
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventario.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev-secret-key'

# Inicializar extensión SQLAlchemy
db.init_app(app)

# Inyectar la fecha y hora actual en los templates
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow}

# Crear tablas base de datos y cargar inventario en contexto
with app.app_context():
    db.create_all()
    inventario = Inventario.cargar_desde_bd()

# Funciones auxiliares para persistencia de datos en archivos dentro de templates/datos

def ensure_templates_datos_folder():
    os.makedirs('templates/datos', exist_ok=True)

def guardar_en_templates_txt(producto):
    ensure_templates_datos_folder()
    with open('templates/datos/dato.txt', 'a', encoding='utf-8') as f:
        f.write(f"{producto.id}|{producto.nombre}|{producto.cantidad}|{producto.precio}|{producto.imagen}|{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

def guardar_en_templates_json(producto):
    ensure_templates_datos_folder()
    datos = []
    try:
        with open('templates/datos/dato.json', 'r', encoding='utf-8') as f:
            datos = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        datos = []
    datos.append({
        'id': producto.id,
        'nombre': producto.nombre,
        'cantidad': producto.cantidad,
        'precio': float(producto.precio),
        'imagen': producto.imagen,
        'fecha_creacion': datetime.now().isoformat()
    })
    with open('templates/datos/dato.json', 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

def guardar_en_templates_csv(producto):
    ensure_templates_datos_folder()
    archivo_existe = os.path.exists('templates/datos/dato.csv')
    with open('templates/datos/dato.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not archivo_existe:
            writer.writerow(['ID', 'Nombre', 'Cantidad', 'Precio', 'Imagen', 'Fecha_Creacion'])
        writer.writerow([
            producto.id,
            producto.nombre,
            producto.cantidad,
            producto.precio,
            producto.imagen,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ])

# Definición de rutas para la aplicación
@app.route('/')
def index():
    return render_template('index.html', title='Inicio')

@app.route('/usuario/')
def usuario(nombre):
    return f'Bienvenido, {nombre}!'

@app.route('/about/')
def about():
    return render_template('about.html', title='Acerca de')

@app.route('/contact/')
def contact():
    return render_template('contact.html', title='Contacto')

# Listado o búsqueda de productos
@app.route('/productos')
def listar_productos():
    q = request.args.get('q', '').strip()
    productos = inventario.buscar_por_nombre(q) if q else inventario.listar_todos()
    return render_template('products/list.html', title='Productos', productos=productos, q=q)

# Crear nuevo producto
@app.route('/productos/nuevo', methods=['GET', 'POST'])
def crear_producto():
    form = ProductoForm()
    if form.validate_on_submit():
        try:
            nuevo_producto = inventario.agregar(
                nombre=form.nombre.data,
                cantidad=form.cantidad.data,
                precio=form.precio.data,
                imagen_file=form.imagen.data
            )
            guardar_en_templates_txt(nuevo_producto)
            guardar_en_templates_json(nuevo_producto)
            guardar_en_templates_csv(nuevo_producto)
            flash('Producto agregado correctamente y guardado en archivos.', 'success')
            return redirect(url_for('listar_productos'))
        except ValueError as e:
            form.nombre.errors.append(str(e))
    return render_template('products/form.html', title='Nuevo producto', form=form, modo='crear')

# Editar producto existente
@app.route('/productos/<int:pid>/editar', methods=['GET', 'POST'])
def editar_producto(pid):
    prod = Producto.query.get_or_404(pid)
    form = ProductoForm(obj=prod)
    if form.validate_on_submit():
        try:
            producto_actualizado = inventario.actualizar(
                id=pid,
                nombre=form.nombre.data,
                cantidad=form.cantidad.data,
                precio=form.precio.data,
                imagen_file=form.imagen.data
            )
            if producto_actualizado:
                guardar_en_templates_txt(producto_actualizado)
                guardar_en_templates_json(producto_actualizado)
                guardar_en_templates_csv(producto_actualizado)
                flash('Producto actualizado y guardado en archivos.', 'success')
                return redirect(url_for('listar_productos'))
        except ValueError as e:
            form.nombre.errors.append(str(e))
    return render_template('products/form.html', title='Editar producto', form=form, modo='editar')

# Eliminar producto
@app.route('/productos/<int:pid>/eliminar', methods=['POST'])
def eliminar_producto(pid):
    ok = inventario.eliminar(pid)
    flash('Producto eliminado.' if ok else 'Producto no encontrado.', 'info' if ok else 'warning')
    return redirect(url_for('listar_productos'))

if __name__ == '__main__':
    app.run(debug=True)
