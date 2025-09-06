from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

class Producto(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), unique=True, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False, default=0)
    precio = db.Column(db.Float, nullable=False, default=0.0)
    imagen = db.Column(db.String(255), nullable=True, default='default.jpg') # ✅ NUEVO CAMPO
    fecha_creacion = db.Column(db.DateTime, default=db.func.current_timestamp()) # ✅ BONUS

    def __repr__(self):
        return f'<Producto {self.id}: {self.nombre}>'

    def to_tuple(self):
        return (self.id, self.nombre, self.cantidad, self.precio, self.imagen)

    def get_image_url(self):
        """Retorna la URL de la imagen del producto"""
        if self.imagen and self.imagen != 'default.jpg':
            return f'/static/uploads/{self.imagen}'
        return '/static/images/default.jpg'
