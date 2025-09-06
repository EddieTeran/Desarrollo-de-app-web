from models import db, Producto
import os
from werkzeug.utils import secure_filename
import uuid
from PIL import Image

class Inventario:
    """
    - Usa un diccionario {id: Producto} para accesos O(1).
    - Mantiene un set con nombres en minúsculas para validar duplicados rápidamente.
    - Maneja subida y procesamiento de imágenes de productos.
    - Devuelve listas ordenadas usando list/tuplas según convenga.
    """

    # Configuración para imágenes
    UPLOAD_FOLDER = 'static/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    MAX_FILE_SIZE = 5 * 1024 * 1024 # 5MB
    IMAGE_SIZE = (400, 300) # Tamaño para redimensionar

    def __init__(self, productos_dict=None):
        self.productos = productos_dict or {}
        self.nombres = set(p.nombre.lower() for p in self.productos.values())
        self._ensure_upload_folder()

    @classmethod
    def cargar_desde_bd(cls):
        productos = Producto.query.all()
        productos_dict = {p.id: p for p in productos}
        return cls(productos_dict)

    def _ensure_upload_folder(self):
        """Crea la carpeta de uploads si no existe"""
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)

    def _allowed_file(self, filename):
        """Verifica si el archivo tiene una extensión permitida"""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS

    def _generate_unique_filename(self, filename):
        """Genera un nombre único para el archivo"""
        if filename and self._allowed_file(filename):
            ext = filename.rsplit('.', 1)[1].lower()
            unique_name = f"{uuid.uuid4().hex}.{ext}"
            return unique_name
        return None

    def _process_image(self, file_path):
        """Procesa y optimiza la imagen"""
        try:
            with Image.open(file_path) as img:
                # Convertir a RGB si es necesario
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                # Redimensionar manteniendo la proporción
                img.thumbnail(self.IMAGE_SIZE, Image.Resampling.LANCZOS)
                # Guardar optimizada
                img.save(file_path, 'JPEG', quality=85, optimize=True)
            return True
        except Exception as e:
            print(f"Error procesando imagen: {e}")
            # Eliminar archivo corrupto
            if os.path.exists(file_path):
                os.remove(file_path)
            return False

    def _save_image(self, file):
        """Guarda la imagen y retorna el nombre del archivo"""
        if not file or file.filename == '':
            return None
        if not self._allowed_file(file.filename):
            raise ValueError('Tipo de archivo no permitido. Use: PNG, JPG, JPEG, GIF, WEBP')
        # Verificar tamaño del archivo
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        if file_size > self.MAX_FILE_SIZE:
            raise ValueError('El archivo es demasiado grande. Máximo 5MB')
        # Generar nombre único y guardar
        filename = self._generate_unique_filename(file.filename)
        if filename:
            file_path = os.path.join(self.UPLOAD_FOLDER, filename)
            file.save(file_path)
            # Procesar imagen
            if self._process_image(file_path):
                return filename
            else:
                raise ValueError('Error al procesar la imagen')
        return None

    def _delete_image(self, imagen_filename):
        """Elimina una imagen del servidor"""
        if imagen_filename and imagen_filename != 'default.jpg':
            file_path = os.path.join(self.UPLOAD_FOLDER, imagen_filename)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Error eliminando imagen: {e}")

    # --- CRUD EXTENDIDO ---
    def agregar(self, nombre: str, cantidad: int, precio: float, imagen_file=None) -> Producto:
        if nombre.lower() in self.nombres:
            raise ValueError('Ya existe un producto con ese nombre.')
        # Procesar imagen si se proporciona
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
            # Si falla, eliminar imagen subida
            if imagen_filename:
                self._delete_image(imagen_filename)
            raise e

    def eliminar(self, id: int) -> bool:
        p = self.productos.get(id) or Producto.query.get(id)
        if not p:
            return False
        # Eliminar imagen asociada
        self._delete_image(p.imagen)
        db.session.delete(p)
        db.session.commit()
        self.productos.pop(id, None)
        self.nombres.discard(p.nombre.lower())
        return True

    def actualizar(self, id: int, nombre=None, cantidad=None, precio=None, imagen_file=None) -> Producto | None:
        p = self.productos.get(id) or Producto.query.get(id)
        if not p:
            return None
        # Validar nombre único si se cambia
        if nombre is not None:
            nuevo = nombre.strip()
            if nuevo.lower() != p.nombre.lower() and nuevo.lower() in self.nombres:
                raise ValueError('Ya existe otro producto con ese nombre.')
        # Procesar nueva imagen si se proporciona
        nueva_imagen = None
        imagen_anterior = p.imagen
        if imagen_file:
            nueva_imagen = self._save_image(imagen_file)
        try:
            # Actualizar campos
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
            # Si se actualizó la imagen, eliminar la anterior
            if nueva_imagen and imagen_anterior != 'default.jpg':
                self._delete_image(imagen_anterior)
            self.productos[p.id] = p
            return p
        except Exception as e:
            # Si falla, eliminar nueva imagen subida
            if nueva_imagen:
                self._delete_image(nueva_imagen)
            raise e

    # --- Consultas con colecciones (sin cambios) ---
    def buscar_por_nombre(self, q: str):
        q = q.lower()
        return sorted(
            [p for p in self.productos.values() if q in p.nombre.lower()],
            key=lambda x: x.nombre
        )

    def listar_todos(self):
        return sorted(self.productos.values(), key=lambda x: x.nombre)

    # --- Métodos adicionales para imágenes ---
    def get_product_image_path(self, product_id: int):
        """Obtiene la ruta completa de la imagen de un producto"""
        p = self.productos.get(product_id)
        if p and p.imagen:
            return os.path.join(self.UPLOAD_FOLDER, p.imagen)
        return None
