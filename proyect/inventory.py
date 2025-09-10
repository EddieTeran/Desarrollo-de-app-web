from models import db, Producto
import os
from werkzeug.utils import secure_filename
import uuid
from PIL import Image

# Clase que gestiona el inventario y operaciones relacionadas
class Inventario:
    # Diccionario para acceso rápido a productos {id: Producto}
    # Set para manejo rápido de nombres y evitar duplicados
    # Métodos para carga, creación, actualización, eliminación, y manejo de imágenes

    # Configuraciones para manejo de imágenes
    UPLOAD_FOLDER = 'static/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    IMAGE_SIZE = (400, 300)  # Tamaño para redimensionar imágenes

    def __init__(self, productos_dict=None):
        self.productos = productos_dict or {}
        self.nombres = set(p.nombre.lower() for p in self.productos.values())
        self._ensure_upload_folder()

    # Carga productos desde base de datos y retorna instancia de Inventario
    @classmethod
    def cargar_desde_bd(cls):
        productos = Producto.query.all()
        productos_dict = {p.id: p for p in productos}
        return cls(productos_dict)

    # Crear carpeta de uploads si no existe
    def _ensure_upload_folder(self):
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)

    # Verifica si un archivo tiene extensión permitida
    def _allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS

    # Genera un nombre único para un archivo
    def _generate_unique_filename(self, filename):
        if filename and self._allowed_file(filename):
            ext = filename.rsplit('.', 1)[1].lower()
            unique_name = f"{uuid.uuid4().hex}.{ext}"
            return unique_name
        return None

    # Procesa y optimiza imagen redimensionándola y guardándola
    def _process_image(self, file_path):
        try:
            with Image.open(file_path) as img:
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                img.thumbnail(self.IMAGE_SIZE, Image.Resampling.LANCZOS)
                img.save(file_path, 'JPEG', quality=85, optimize=True)
            return True
        except Exception as e:
            print(f"Error procesando imagen: {e}")
            if os.path.exists(file_path):
                os.remove(file_path)
            return False

    # Guarda archivo de imagen subido, retornando el nombre generado unico
    def _save_image(self, file):
        if file is None:
            return None
        if isinstance(file, str):
            return None
        if not hasattr(file, 'filename') or file.filename == '':
            return None
        if not self._allowed_file(file.filename):
            raise ValueError('Tipo de archivo no permitido. Use: PNG, JPG, JPEG, GIF, WEBP')
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        if file_size > self.MAX_FILE_SIZE:
            raise ValueError('El archivo es demasiado grande. Máximo 5MB')
        filename = self._generate_unique_filename(file.filename)
        if filename:
            file_path = os.path.join(self.UPLOAD_FOLDER, filename)
            file.save(file_path)
            if self._process_image(file_path):
                return filename
            else:
                raise ValueError('Error al procesar la imagen')
        return None

    # Elimina un archivo de imagen del servidor salvo la default
    def _delete_image(self, imagen_filename):
        if imagen_filename and imagen_filename != 'default.jpg':
            file_path = os.path.join(self.UPLOAD_FOLDER, imagen_filename)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Error eliminando imagen: {e}")

    # Agrega un producto nuevo al inventario y base de datos
    def agregar(self, nombre: str, cantidad: int, precio: float, imagen_file=None) -> Producto:
        if nombre.lower() in self.nombres:
            raise ValueError('Ya existe un producto con ese nombre.')
        imagen_filename = None
        if imagen_file:
            imagen_filename = self._save_image(imagen_file)
        p = Producto(
            nombre=nombre.strip(),
            cantidad=int(cantidad),
            precio=float(precio),
            imagen=imagen_filename or 'default.jpg'
        )
        try:
            db.session.add(p)
            db.session.commit()
            self.productos[p.id] = p
            self.nombres.add(p.nombre.lower())
            return p
        except Exception as e:
            if imagen_filename:
                self._delete_image(imagen_filename)
            raise e

    # Elimina producto por id, eliminando imagen si aplica
    def eliminar(self, id: int) -> bool:
        p = self.productos.get(id) or Producto.query.get(id)
        if not p:
            return False
        self._delete_image(p.imagen)
        db.session.delete(p)
        db.session.commit()
        self.productos.pop(id, None)
        self.nombres.discard(p.nombre.lower())
        return True

    # Actualiza producto por id con nuevos valores y bytes de imagen
    def actualizar(self, id: int, nombre=None, cantidad=None, precio=None, imagen_file=None) -> Producto | None:
        p = self.productos.get(id) or Producto.query.get(id)
        if not p:
            return None
        if nombre is not None:
            nuevo = nombre.strip()
            if nuevo.lower() != p.nombre.lower() and nuevo.lower() in self.nombres:
                raise ValueError('Ya existe otro producto con ese nombre.')
        nueva_imagen = None
        imagen_anterior = p.imagen
        if imagen_file:
            nueva_imagen = self._save_image(imagen_file)
        try:
            if nombre is not None:
                self.nombres.discard(p.nombre.lower())
                p.nombre = nombre.strip()
                self.nombres.add(p.nombre.lower())
            if cantidad is not None:
                p.cantidad = int(cantidad)
            if precio is not None:
                p.precio = float(precio)
            if nueva_imagen:
                p.imagen = nueva_imagen
            db.session.commit()
            if nueva_imagen and imagen_anterior != 'default.jpg':
                self._delete_image(imagen_anterior)
            self.productos[p.id] = p
            return p
        except Exception as e:
            if nueva_imagen:
                self._delete_image(nueva_imagen)
            raise e

    # Busca productos que contengan texto q en el nombre (en minúsculas)
    def buscar_por_nombre(self, q: str):
        q = q.lower()
        return sorted(
            [p for p in self.productos.values() if q in p.nombre.lower()],
            key=lambda x: x.nombre
        )

    # Retorna lista de todos los productos ordenados por nombre
    def listar_todos(self):
        return sorted(self.productos.values(), key=lambda x: x.nombre)

    # Ruta absoluta de imagen del producto
    def get_product_image_path(self, product_id: int):
        p = self.productos.get(product_id)
        if p and p.imagen:
            return os.path.join(self.UPLOAD_FOLDER, p.imagen)
        return None
