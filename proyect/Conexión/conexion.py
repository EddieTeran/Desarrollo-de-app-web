# Conexión/conexion.py
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

class MySQLConnection:
    def __init__(self):
        self.connection = None
        # Configuración de la conexión usando variables de entorno
        self.config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '3307')),  # Tu puerto 330
            'database': os.getenv('DB_NAME', 'dbcaprichos'),
            'user': os.getenv('DB_USER', 'root'),
            'password': '000000',  # <-- entre comillas
            'autocommit': True,
            'charset': 'utf8mb4'
        }
    
    def get_connection(self):
        """Obtiene una conexión a la base de datos MySQL"""
        try:
            if self.connection is None or not self.connection.is_connected():
                self.connection = mysql.connector.connect(**self.config)
                print("✅ Conexión a MySQL establecida correctamente")
            return self.connection
        except Error as e:
            print(f" Error conectando a MySQL: {e}")
            return None
    
    def close_connection(self):
        """Cierra la conexión a la base de datos"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.connection = None
            print("🔒 Conexión a MySQL cerrada")

# Instancia global de la conexión
mysql_connection = MySQLConnection()

def get_db():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='000000', 
        database='dbcaprichos',
        port=3307
    )

def close_db():
    """Función para cerrar la conexión desde otros archivos"""
    mysql_connection.close_connection()

def execute_query(query, params=None):
    """Ejecuta una consulta SQL y devuelve los resultados"""
    connection = get_db()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params)
            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                cursor.close()
                return results
            else:
                connection.commit()
                cursor.close()
                return True
        except Error as e:
            print(f" Error ejecutando consulta: {e}")
            return None
    return None
