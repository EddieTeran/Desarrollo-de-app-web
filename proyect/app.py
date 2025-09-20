from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime
import json
import csv
import os
from models import db, Producto, Usuario
from forms import ProductoForm, LoginForm, RegistroForm
from inventory import Inventario
from Conexión.conexion import get_db, close_db
import mysql.connector
from mysql.connector import Error
from Conexión.conexion import get_db, close_db, execute_query

# Inicializamos la aplicación Flask
app = Flask(__name__)

# Configuración de base de datos y seguridad
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:000000@localhost:3307/dbcaprichos'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev-secret-key'

# Inicializar extensión SQLAlchemy
db.init_app(app)

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, inicia sesión para acceder a esta página.'
login_manager.login_message_category = 'info'

# Función para cargar usuario (requerida por Flask-Login)
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

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

# Eliminar producto existente
@app.route('/productos/<int:pid>/eliminar', methods=['POST'])
def eliminar_producto(pid):
    ok = inventario.eliminar(pid)
    flash('Producto eliminado.' if ok else 'Producto no encontrado.', 'info' if ok else 'warning')
    return redirect(url_for('listar_productos'))

# ==================== RUTAS DE AUTENTICACIÓN ====================

# Ruta para registro de usuarios
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistroForm()
    if form.validate_on_submit():
        try:
            # Crear nuevo usuario
            nuevo_usuario = Usuario(
                username=form.username.data,
                email=form.email.data,
                nombre_completo=form.nombre_completo.data
            )
            nuevo_usuario.set_password(form.password.data)
            
            # Guardar en la base de datos
            db.session.add(nuevo_usuario)
            db.session.commit()
            
            flash('¡Registro exitoso! Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error al crear la cuenta. Inténtalo de nuevo.', 'error')
            print(f"Error en registro: {e}")
    
    return render_template('auth/registro.html', title='Registro', form=form)

# Ruta para inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Buscar usuario por username o email
        usuario = Usuario.get_by_username(form.username.data)
        if not usuario:
            usuario = Usuario.get_by_email(form.username.data)
        
        if usuario and usuario.check_password(form.password.data):
            if usuario.is_active():
                login_user(usuario, remember=form.remember_me.data)
                
                # Actualizar último acceso
                usuario.ultimo_acceso = datetime.utcnow()
                db.session.commit()
                
                next_page = request.args.get('next')
                if not next_page or not next_page.startswith('/'):
                    next_page = url_for('index')
                
                flash(f'¡Bienvenido, {usuario.nombre_completo}!', 'success')
                return redirect(next_page)
            else:
                flash('Tu cuenta está desactivada. Contacta al administrador.', 'warning')
        else:
            flash('Credenciales incorrectas. Verifica tu usuario y contraseña.', 'error')
    
    return render_template('auth/login.html', title='Iniciar Sesión', form=form)

# Ruta para cerrar sesión
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('index'))

# Ruta protegida de ejemplo
@app.route('/perfil')
@login_required
def perfil():
    return render_template('auth/perfil.html', title='Mi Perfil', usuario=current_user)

# Ruta de prueba de conexión a MySQL
@app.route('/test_db')
def test_db():
    connection = None
    try:
        connection = get_db()
        if connection and connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            cursor.close()
            port = connection.server_port 
            return f"""
            <h1> Conexión exitosa a MySQL</h1>
            <p><strong>Versión de MySQL:</strong> {version[0]}</p>
            <p><strong>Puerto:</strong> {port}</p>
            <p><strong>Estado:</strong> Conectado correctamente</p>
            <a href="/">Volver al inicio</a>
            """
        else:
            return """
            <h1> Error de conexión</h1>
            <p>No se pudo conectar a la base de datos MySQL</p>
            <a href="/">Volver al inicio</a>
            """
    except Error as e:
        return f"""
        <h1> Error de conexión</h1>
        <p><strong>Error:</strong> {str(e)}</p>
        <a href="/">Volver al inicio</a>
        """
    finally:
        if connection and connection.is_connected():
            connection.close()

# Manejador para cerrar conexiones al finalizar la app
@app.teardown_appcontext
def close_db_connection(error):
    close_db()


if __name__ == '__main__':
    app.run(debug=True)
