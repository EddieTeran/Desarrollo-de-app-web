from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import os

# Inicializamos la extensión SQLAlchemy
db = SQLAlchemy()

# Definición de la clase Producto que representa la tabla productos en la base de datos
class Producto(db.Model):
    __tablename__ = 'productos'

    # Columnas de la tabla
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), unique=True, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False, default=0)
    precio = db.Column(db.Float, nullable=False, default=0.0)
    imagen = db.Column(db.String(255), nullable=True, default='default.jpg')
    fecha_creacion = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Representación en string del objeto (vacía por ahora)
    def __repr__(self):
        return f''

    # Devuelve una tupla con los atributos principales
    def to_tuple(self):
        return (self.id, self.nombre, self.cantidad, self.precio, self.imagen)

    # Obtiene la URL para mostrar la imagen del producto
    def get_image_url(self):
        if self.imagen and self.imagen != 'default.jpg':
            return f'/static/uploads/{self.imagen}'
        return '/static/images/default.jpg'

# Definición de la clase Usuario que representa la tabla usuarios en la base de datos
class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    # Columnas de la tabla
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nombre_completo = db.Column(db.String(120), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.DateTime, default=db.func.current_timestamp())
    ultimo_acceso = db.Column(db.DateTime, nullable=True)

    # Representación en string del objeto
    def __repr__(self):
        return f'<Usuario {self.username}>'

    # Establecer contraseña (hash)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Verificar contraseña
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Verificar si el usuario está activo
    def is_active(self):
        return self.activo

    # Obtener ID del usuario (requerido por Flask-Login)
    def get_id(self):
        return str(self.id)

    # Método para obtener usuario por username
    @staticmethod
    def get_by_username(username):
        return Usuario.query.filter_by(username=username).first()

    # Método para obtener usuario por email
    @staticmethod
    def get_by_email(email):
        return Usuario.query.filter_by(email=email).first()
