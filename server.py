import asyncio
from Crypto.Cipher import AES
from dotenv import load_dotenv
import os, ssl
from pymysql import NULL
from connectDB import connectDB, getUsers, consultarSaldo, transferenciaSaldo
import werkzeug.security

load_dotenv()

HOST = "0.0.0.0"
PORT = os.getenv('PORT')
CERTIFICATE_PATH = os.getenv('CERTIFICATE_PATH')
CERTIFICATE_KEY = os.getenv('KEY_PATH')
shared_key = os.getenv('CRYPTOKEY')
remote_addresses = list()
if not shared_key:
    raise ValueError("La variable de entorno SHARED_KEY no está definida en el archivo .env")
encoded_key = shared_key.encode("utf-8")
trunk_encoded_key = encoded_key[:16]
lock = asyncio.Lock()

def showmenu(logged_user):
    msg = f"""Bienvenido a tu banca {logged_user[2]}, elije una de las siguientes opciones para continuar:
    1) Consultar tu saldo.
    2) Realizar una transferencia 
    3) Salir.
    Opción a elegir: """
    return msg

async def handle_clients(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    # conn, cursor = connectDB()
    connected_address = writer.get_extra_info('peername')
    if connected_address[0] in remote_addresses:
        print(f"cliente {connected_address[0]} ya está conectado, nueva conexión rechazada")
        cipher = AES.new(trunk_encoded_key,AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest("\n Usted ya tiene un sesión activa Salir".encode())
        writer.write(cipher.nonce + ciphertext)
        await writer.drain()
        writer.close()
        await writer.wait_closed()
        return
    else:
        print(f"Nueva conexión recibida desde la IP {connected_address[0]}") 
        remote_addresses.append(connected_address[0])

    msg, islogged, logged_user  = await login(reader,writer)
    if islogged:
        # getUsers(cursor)
        # showmenu(logged_user)
        print(f"cliente {connected_address[0]} realiza un login exitoso en la cuenta: {logged_user[2]}")
        menu = showmenu(logged_user)
        cipher = AES.new(trunk_encoded_key,AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(menu.encode())
        writer.write(cipher.nonce + ciphertext)
        await writer.drain()
        option = await reader.read(1024)
        cipher = AES.new(trunk_encoded_key, AES.MODE_EAX, nonce=option[:16])
        option_str = cipher.decrypt(option[16:])
        while (option_str.decode() != "3"):
            if (option_str.decode() == "1"):
                async with lock:
                    conn, cursor = connectDB()
                    print(f"procesando consulta de saldo del cliente {connected_address[0]}")
                    msg = consultarSaldo(logged_user,cursor)
                    cursor.close()
                    conn.close()
                print(f"consulta de saldo del cliente {connected_address[0]} realizada con éxito")
                cipher = AES.new(trunk_encoded_key,AES.MODE_EAX)
                ciphertext, tag = cipher.encrypt_and_digest((f"\n {msg} \n\n"+ menu).encode())
                writer.write(cipher.nonce + ciphertext)
                await writer.drain()
                option = await reader.read(1024)
                cipher = AES.new(trunk_encoded_key, AES.MODE_EAX, nonce=option[:16])
                option_str = cipher.decrypt(option[16:])
            elif (option_str.decode() == "2"):
                cipher = AES.new(trunk_encoded_key,AES.MODE_EAX)
                ciphertext, tag = cipher.encrypt_and_digest("\n ingresa la cantidad que quieras enviar: ".encode())
                writer.write(cipher.nonce + ciphertext)
                await writer.drain()
                cantidad = await reader.read(1024)
                cipher = AES.new(trunk_encoded_key, AES.MODE_EAX, nonce=cantidad[:16])
                cantidad_str = cipher.decrypt(cantidad[16:])
                cipher = AES.new(trunk_encoded_key,AES.MODE_EAX)
                ciphertext, tag = cipher.encrypt_and_digest("ingresa la cuenta clabe destino: ".encode())
                writer.write(cipher.nonce + ciphertext)
                await writer.drain()
                cuenta_dest = await reader.read(1024)
                cipher = AES.new(trunk_encoded_key, AES.MODE_EAX, nonce=cuenta_dest[:16])
                cuenta_dest_str = cipher.decrypt(cuenta_dest[16:])
                async with lock:
                    conn, cursor = connectDB()
                    print(f"procesando transferencia del cliente {connected_address[0]}")
                    msg = transferenciaSaldo(logged_user,conn,cursor,cantidad_str.decode(),cuenta_dest_str.decode())
                    cursor.close()
                    conn.close()
                print(f"transferencia de saldo exitosa del cliente {connected_address[0]}")
                cipher = AES.new(trunk_encoded_key,AES.MODE_EAX)
                ciphertext, tag = cipher.encrypt_and_digest((f"\n {msg} \n\n"+ menu).encode())
                writer.write(cipher.nonce + ciphertext)
                await writer.drain()
                option = await reader.read(1024)
                cipher = AES.new(trunk_encoded_key, AES.MODE_EAX, nonce=option[:16])
                option_str = cipher.decrypt(option[16:])
            else:
                cipher = AES.new(trunk_encoded_key,AES.MODE_EAX)
                ciphertext, tag = cipher.encrypt_and_digest(("Esa no es una opción valida \n" + menu).encode())
                writer.write(cipher.nonce + ciphertext)
                await writer.drain()
                option = await reader.read(1024)
                cipher = AES.new(trunk_encoded_key, AES.MODE_EAX, nonce=option[:16])
                option_str = cipher.decrypt(option[16:])
        
        msg = "Gracias por utilizar nuestros servicios =)"

    remote_addresses.remove(connected_address[0])            
    cipher = AES.new(trunk_encoded_key,AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest((msg + " Salir").encode())
    writer.write(cipher.nonce + ciphertext)
    print(f"se ha cerrado la conexión con el cliente {connected_address[0]}")
    writer.close()
    await writer.wait_closed()

async def login(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    conn, cursor = connectDB()
    cipher = AES.new(trunk_encoded_key,AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest("Para iniciar por favor introduce tu nombre de usuario: ".encode())
    writer.write(cipher.nonce + ciphertext)
    await writer.drain()
    username = await reader.read(1024)
    cipher = AES.new(trunk_encoded_key, AES.MODE_EAX, nonce=username[:16])
    username_str = cipher.decrypt(username[16:])
    #Busca al usuario en la base de datos.
    cursor.execute("SELECT * FROM usuarios WHERE username=%s", (username_str.decode(),))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user:
        print(f"{user[2]} encontrado")
        cipher = AES.new(trunk_encoded_key,AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest("Ahora introduce tu contraseña: ".encode())
        writer.write(cipher.nonce + ciphertext)
        await writer.drain()
        password = await reader.read(1024)
        cipher = AES.new(trunk_encoded_key, AES.MODE_EAX, nonce=password[:16])
        password_str = cipher.decrypt(password[16:])
        #Verifica que la contraseña del usuario sea válida.
        if werkzeug.security.check_password_hash(user[3], password_str.decode()) == True:
            msg = "Ingreso exitoso"
            # print(msg)
            return msg, True, user
        else:
            msg = "Contraseña incorrecta"
            # print(msg)
            return msg, False, None
    else:
        
        msg = "Usuario no encontrado =("
        # print(msg)
        return msg, False, None
        
async def run_server():
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile=CERTIFICATE_PATH, keyfile=CERTIFICATE_KEY)
    server = await asyncio.start_server(handle_clients,HOST,PORT, ssl=ssl_context)

    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(run_server())

