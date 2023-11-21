from time import sleep
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
    print("Conexión establecida con la base de datos")
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
  print("ID_usuario, username, ownerAccount, password, balance, clabe")
  for usuario in usuarios:
    print(usuario)

#Función que realiza una consulta de saldo:
def consultarSaldo(user,cursor):
    cursor.execute("SELECT balance FROM usuarios WHERE ID_usuario = %s", (user[0],))
    saldo = cursor.fetchone()
    if saldo:
      return f"Tu saldo es {saldo[0]}"
    return "Error: No tiene saldo con nosotros"

#Función que realiza una transferencia de saldo:
def transferenciaSaldo(user,conn,cursor,cantidad,cuenta_dest):
  try:
    cursor.execute("SELECT balance FROM usuarios WHERE ID_usuario = %s", (user[0],))
    saldo_src = cursor.fetchone()[0]
    new_saldo_src = saldo_src - float(cantidad)
    if (new_saldo_src < 0):
      return "Error: No se puede procesar la transferencia debido a que no tiene suficientes fondos"
    cursor.execute("SELECT balance FROM usuarios WHERE clabe = %s", (cuenta_dest,))
    saldo_dest = cursor.fetchone()[0]
    if saldo_dest:
      new_saldo_dest = saldo_dest + float(cantidad)
      cursor.execute("UPDATE usuarios SET balance = %s WHERE clabe=%s", (new_saldo_dest,cuenta_dest))
      cursor.execute("UPDATE usuarios SET balance = %s WHERE ID_usuario =%s", (new_saldo_src,user[0]))
      conn.commit()
      return f"Transferencia de la cuenta {user[5]} hacia la cuenta {cuenta_dest} realizada exitosamente"
    return "Error: No se encontró la cuenta destino"
  except Exception as ex:
    return f"Error: {ex}"
