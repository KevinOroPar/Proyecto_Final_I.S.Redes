import mysql.connector
from mysql.connector import errorcode

# Configuración de la conexión a la bd.
config = {
  'host':'redessem10.mysql.database.azure.com',
  'user':'ciberadmin',
  'password':'r3g3n9003#',
  'database':'bancoksystems'
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
