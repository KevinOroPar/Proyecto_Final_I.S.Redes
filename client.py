import asyncio
from os import write
from dotenv import load_dotenv
from Crypto.Cipher import AES
import os, re, ssl

from server import CERTIFICATE_PATH

load_dotenv()

HOST = os.environ.get('HOST')
PORT = os.environ.get('PORT')
shared_key = os.getenv('CRYPTOKEY')
if not shared_key:
    raise ValueError("La variable de entorno SHARED_KEY no está definida en el archivo .env")
encoded_key = shared_key.encode()
trunk_encoded_key = encoded_key[:16]
patron = re.compile(r'.*Salir$')

async def run_client() -> None:
        ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ssl_context.load_verify_locations(CERTIFICATE_PATH)
        reader, writer = await asyncio.open_connection(HOST, PORT, ssl=ssl_context)

        while True:
            data = await reader.read(1024)
            cipher = AES.new(trunk_encoded_key, AES.MODE_EAX, nonce=data[:16])
            message = cipher.decrypt(data[16:])
            msg = message.decode()
            ismatch = patron.search(msg)
            if ismatch:
                writer.close()
                await writer.wait_closed()
                print(msg[0:-5])
                print("Conexión cerrada por el servidor =(")
                break
            resp = input(msg)
            cipher = AES.new(trunk_encoded_key,AES.MODE_EAX)
            ciphertext, tag = cipher.encrypt_and_digest(resp.encode())
            writer.write(cipher.nonce + ciphertext)
            await writer.drain()
             

if __name__ == '__main__':
    asyncio.run(run_client())