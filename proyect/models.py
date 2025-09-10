from flask_sqlalchemy import SQLAlchemy
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
