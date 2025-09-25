

from flask import Flask
from models import db, Usuario, Producto
from Conexión.conexion import get_db, close_db
import mysql.connector
from mysql.connector import Error

# Configuración de la aplicación
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:000000@localhost:3307/dbcaprichos'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

class DatabaseManager:
    def __init__(self):
        self.app = app
        
    def show_menu(self):
        """Muestra el menú principal"""
        print("\n" + "="*50)
        print("🗄️  GESTOR DE BASE DE DATOS - DBCAPRICHOS")
        print("="*50)
        print("1. 👥 Gestionar Usuarios")
        print("2. 📦 Gestionar Productos")
        print("3. 📊 Ver Estadísticas")
        print("4. 🔍 Consultas Personalizadas")
        print("5. 🗑️  Limpiar Base de Datos")
        print("6. ❌ Salir")
        print("="*50)
        
    def manage_users(self):
        """Gestiona usuarios"""
        while True:
            print("\n👥 GESTIÓN DE USUARIOS")
            print("1. Ver todos los usuarios")
            print("2. Crear nuevo usuario")
            print("3. Buscar usuario")
            print("4. Eliminar usuario")
            print("5. Volver al menú principal")
            
            choice = input("\nSelecciona una opción: ")
            
            if choice == "1":
                self.show_all_users()
            elif choice == "2":
                self.create_user()
            elif choice == "3":
                self.search_user()
            elif choice == "4":
                self.delete_user()
            elif choice == "5":
                break
            else:
                print("❌ Opción inválida")
    
    def manage_products(self):
        """Gestiona productos"""
        while True:
            print("\n📦 GESTIÓN DE PRODUCTOS")
            print("1. Ver todos los productos")
            print("2. Crear nuevo producto")
            print("3. Buscar producto")
            print("4. Eliminar producto")
            print("5. Actualizar producto")
            print("6. Volver al menú principal")
            
            choice = input("\nSelecciona una opción: ")
            
            if choice == "1":
                self.show_all_products()
            elif choice == "2":
                self.create_product()
            elif choice == "3":
                self.search_product()
            elif choice == "4":
                self.delete_product()
            elif choice == "5":
                self.update_product()
            elif choice == "6":
                break
            else:
                print("❌ Opción inválida")
    
    def show_all_users(self):
        """Muestra todos los usuarios"""
        with self.app.app_context():
            users = Usuario.query.all()
            if not users:
                print("📭 No hay usuarios registrados")
                return
            
            print(f"\n👥 USUARIOS REGISTRADOS ({len(users)}):")
            print("-" * 80)
            for user in users:
                print(f"ID: {user.id}")
                print(f"Username: {user.username}")
                print(f"Email: {user.email}")
                print(f"Nombre: {user.nombre_completo}")
                print(f"Activo: {'Sí' if user.activo else 'No'}")
                print(f"Registro: {user.fecha_registro}")
                print("-" * 80)
    
    def create_user(self):
        """Crea un nuevo usuario"""
        print("\n➕ CREAR NUEVO USUARIO")
        username = input("Username: ")
        email = input("Email: ")
        nombre_completo = input("Nombre completo: ")
        password = input("Contraseña: ")
        
        try:
            with self.app.app_context():
                # Verificar si ya existe
                if Usuario.get_by_username(username):
                    print("❌ El username ya existe")
                    return
                if Usuario.get_by_email(email):
                    print("❌ El email ya está registrado")
                    return
                
                # Crear usuario
                new_user = Usuario(
                    username=username,
                    email=email,
                    nombre_completo=nombre_completo
                )
                new_user.set_password(password)
                
                db.session.add(new_user)
                db.session.commit()
                print("✅ Usuario creado exitosamente")
                
        except Exception as e:
            print(f"❌ Error creando usuario: {e}")
    
    def search_user(self):
        """Busca un usuario"""
        search_term = input("\n🔍 Buscar usuario (username o email): ")
        
        with self.app.app_context():
            user = Usuario.get_by_username(search_term)
            if not user:
                user = Usuario.get_by_email(search_term)
            
            if user:
                print(f"\n✅ Usuario encontrado:")
                print(f"ID: {user.id}")
                print(f"Username: {user.username}")
                print(f"Email: {user.email}")
                print(f"Nombre: {user.nombre_completo}")
                print(f"Activo: {'Sí' if user.activo else 'No'}")
            else:
                print("❌ Usuario no encontrado")
    
    def delete_user(self):
        """Elimina un usuario"""
        user_id = input("\n🗑️ ID del usuario a eliminar: ")
        
        try:
            with self.app.app_context():
                user = Usuario.query.get(int(user_id))
                if user:
                    confirm = input(f"¿Eliminar usuario '{user.username}'? (s/n): ")
                    if confirm.lower() == 's':
                        db.session.delete(user)
                        db.session.commit()
                        print("✅ Usuario eliminado")
                    else:
                        print("❌ Operación cancelada")
                else:
                    print("❌ Usuario no encontrado")
        except ValueError:
            print("❌ ID inválido")
        except Exception as e:
            print(f"❌ Error eliminando usuario: {e}")
    
    def show_all_products(self):
        """Muestra todos los productos"""
        with self.app.app_context():
            products = Producto.query.all()
            if not products:
                print("📭 No hay productos registrados")
                return
            
            print(f"\n📦 PRODUCTOS REGISTRADOS ({len(products)}):")
            print("-" * 80)
            for product in products:
                print(f"ID: {product.id}")
                print(f"Nombre: {product.nombre}")
                print(f"Cantidad: {product.cantidad}")
                print(f"Precio: ${product.precio}")
                print(f"Imagen: {product.imagen}")
                print(f"Fecha: {product.fecha_creacion}")
                print("-" * 80)
    
    def create_product(self):
        """Crea un nuevo producto"""
        print("\n➕ CREAR NUEVO PRODUCTO")
        nombre = input("Nombre del producto: ")
        cantidad = int(input("Cantidad: "))
        precio = float(input("Precio: $"))
        
        try:
            with self.app.app_context():
                # Verificar si ya existe
                existing = Producto.query.filter_by(nombre=nombre).first()
                if existing:
                    print("❌ Ya existe un producto con ese nombre")
                    return
                
                # Crear producto
                new_product = Producto(
                    nombre=nombre,
                    cantidad=cantidad,
                    precio=precio,
                    imagen='default.jpg'
                )
                
                db.session.add(new_product)
                db.session.commit()
                print("✅ Producto creado exitosamente")
                
        except Exception as e:
            print(f"❌ Error creando producto: {e}")
    
    def search_product(self):
        """Busca un producto"""
        search_term = input("\n🔍 Buscar producto (nombre): ")
        
        with self.app.app_context():
            products = Producto.query.filter(Producto.nombre.contains(search_term)).all()
            
            if products:
                print(f"\n✅ Productos encontrados ({len(products)}):")
                for product in products:
                    print(f"ID: {product.id} - {product.nombre} - ${product.precio}")
            else:
                print("❌ No se encontraron productos")
    
    def delete_product(self):
        """Elimina un producto"""
        product_id = input("\n🗑️ ID del producto a eliminar: ")
        
        try:
            with self.app.app_context():
                product = Producto.query.get(int(product_id))
                if product:
                    confirm = input(f"¿Eliminar producto '{product.nombre}'? (s/n): ")
                    if confirm.lower() == 's':
                        db.session.delete(product)
                        db.session.commit()
                        print("✅ Producto eliminado")
                    else:
                        print("❌ Operación cancelada")
                else:
                    print("❌ Producto no encontrado")
        except ValueError:
            print("❌ ID inválido")
        except Exception as e:
            print(f"❌ Error eliminando producto: {e}")
    
    def update_product(self):
        """Actualiza un producto"""
        product_id = input("\n✏️ ID del producto a actualizar: ")
        
        try:
            with self.app.app_context():
                product = Producto.query.get(int(product_id))
                if not product:
                    print("❌ Producto no encontrado")
                    return
                
                print(f"\nProducto actual: {product.nombre}")
                print("Deja en blanco para mantener el valor actual")
                
                new_nombre = input(f"Nuevo nombre [{product.nombre}]: ") or product.nombre
                new_cantidad = input(f"Nueva cantidad [{product.cantidad}]: ") or product.cantidad
                new_precio = input(f"Nuevo precio [${product.precio}]: ") or product.precio
                
                product.nombre = new_nombre
                product.cantidad = int(new_cantidad)
                product.precio = float(new_precio)
                
                db.session.commit()
                print("✅ Producto actualizado")
                
        except ValueError:
            print("❌ ID o valores inválidos")
        except Exception as e:
            print(f"❌ Error actualizando producto: {e}")
    
    def show_statistics(self):
        """Muestra estadísticas de la base de datos"""
        with self.app.app_context():
            user_count = Usuario.query.count()
            product_count = Producto.query.count()
            
            print(f"\n📊 ESTADÍSTICAS DE LA BASE DE DATOS")
            print("-" * 40)
            print(f"👥 Total de usuarios: {user_count}")
            print(f"📦 Total de productos: {product_count}")
            
            if product_count > 0:
                products = Producto.query.all()
                total_value = sum(p.precio * p.cantidad for p in products)
                print(f"💰 Valor total del inventario: ${total_value:.2f}")
                
                # Producto más caro
                expensive = max(products, key=lambda p: p.precio)
                print(f"💎 Producto más caro: {expensive.nombre} (${expensive.precio})")
                
                # Producto con más stock
                most_stock = max(products, key=lambda p: p.cantidad)
                print(f"📈 Mayor stock: {most_stock.nombre} ({most_stock.cantidad} unidades)")
    
    def custom_query(self):
        """Ejecuta consultas personalizadas"""
        print("\n🔍 CONSULTAS PERSONALIZADAS")
        print("Ejemplos de consultas:")
        print("1. SELECT * FROM usuarios WHERE activo = 1")
        print("2. SELECT * FROM productos WHERE precio > 50")
        print("3. SELECT COUNT(*) FROM productos")
        
        query = input("\nIngresa tu consulta SQL: ")
        
        try:
            connection = get_db()
            if connection and connection.is_connected():
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query)
                
                if query.strip().upper().startswith('SELECT'):
                    results = cursor.fetchall()
                    if results:
                        print(f"\n✅ Resultados ({len(results)} filas):")
                        for row in results:
                            print(row)
                    else:
                        print("📭 No se encontraron resultados")
                else:
                    connection.commit()
                    print("✅ Consulta ejecutada exitosamente")
                
                cursor.close()
            else:
                print("❌ Error de conexión")
                
        except Error as e:
            print(f"❌ Error en la consulta: {e}")
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    def clean_database(self):
        """Limpia la base de datos"""
        print("\n🗑️ LIMPIAR BASE DE DATOS")
        print("⚠️  ADVERTENCIA: Esta acción eliminará TODOS los datos")
        confirm = input("¿Estás seguro? Escribe 'ELIMINAR' para confirmar: ")
        
        if confirm == "ELIMINAR":
            try:
                with self.app.app_context():
                    # Eliminar todos los productos
                    Producto.query.delete()
                    # Eliminar todos los usuarios
                    Usuario.query.delete()
                    db.session.commit()
                    print("✅ Base de datos limpiada")
            except Exception as e:
                print(f"❌ Error limpiando base de datos: {e}")
        else:
            print("❌ Operación cancelada")
    
    def run(self):
        """Ejecuta el gestor de base de datos"""
        print("🚀 Iniciando Gestor de Base de Datos...")
        
        # Verificar conexión
        try:
            with self.app.app_context():
                Usuario.query.count()
                print("✅ Conexión a la base de datos exitosa")
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return
        
        while True:
            self.show_menu()
            choice = input("\nSelecciona una opción: ")
            
            if choice == "1":
                self.manage_users()
            elif choice == "2":
                self.manage_products()
            elif choice == "3":
                self.show_statistics()
            elif choice == "4":
                self.custom_query()
            elif choice == "5":
                self.clean_database()
            elif choice == "6":
                print("👋 ¡Hasta luego!")
                break
            else:
                print("❌ Opción inválida")

if __name__ == "__main__":
    manager = DatabaseManager()
    manager.run()


