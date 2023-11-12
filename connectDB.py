import mysql.connector
from mysql.connector import errorcode
from dotenv import load_dotenv
import os

# Configuración de la conexión a la bd.
load_dotenv()
config = {
  'host': os.getenv('DB_HOST'),
  'user': os.getenv('DB_ADMIN'),
  'password': os.getenv('DB_PASS'),
  'database': os.getenv('DATABASE')
}

#Función que realiza la conexión a la bd y devuelve un cursor para su manipulación.
def connectDB():
  try:
    conn = mysql.connector.connect(**config)
    print("Conexión establecida")
  except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
      print("Usuario o contraseña incorrectos.")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
      print("La base de datos no existe.")
    else:
      print(err)
  else:
    cursor = conn.cursor()
    return conn, cursor

#Función que muestra a los usuarios registrdos en la bd.  
def getUsers(cursor):
  cursor.execute("SELECT * FROM usuarios")
  usuarios = cursor.fetchall()
  print("ID, username, nombre completo, contraseña, saldo")
  for usuario in usuarios:
    print(usuario)