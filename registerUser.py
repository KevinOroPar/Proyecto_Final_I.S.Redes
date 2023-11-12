import werkzeug.security
from connectDB import connectDB

#Se apertura la conxión con la base de datos.
conn, cursor = connectDB()
#Se piden datos para insertar.
owner = input('Ingrese nombre y un apellido: ')
username = input('Ingrese nombre de usuario: ')
password = input('Ingrese contraseña: ')
balance = float(input('Ingrese saldo inicial: '))

#Encriptación de la contraseña.
hashed_password = werkzeug.security.generate_password_hash(password)
#Inserción del usuario en la bd.
cursor.execute("INSERT INTO usuarios(username, ownerAccount, password, balance) VALUES (%s, %s, %s,%s);", (username, owner, hashed_password, balance)) 
conn.commit()
cursor.close()
conn.close()
print("Usuario agregado")
