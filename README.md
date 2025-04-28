# Secure Communication and User Management System

## Overview 📡
This project was developed as the final project of the course **Communications and Networks Security**.  
It demonstrates a secure client-server communication using:

- **SSL Certificates** for secure socket connections.
- **AES Encryption** for secure data exchange.
- **Python Sockets** for networking.
- **SQL Database** for secure user data management.

## Features 👾
- Establishment of SSL/TLS-encrypted socket communication between server and clients.
- Implementation of AES encryption for sensitive data transmissions.
- User authentication and management using a SQL database.
- User operations include account creation, login, balance inquiry, and secure transaction handling.

## Technologies Used 💻
- **Python** (socket programming, cryptography, SSL)
- **SQL** (for database operations)
- **OpenSSL** (for generating certificates)

## Database Structure 📓

The project uses a single table with the following fields:
- `owner` — Full name of the account owner
- `username` — Username for login
- `password` — (Encrypted) password for authentication
- `balance` — Current account balance
- `clabe` — Unique account number

## Quickstart ⚡

1. **Install required libraries:**
    ```bash
    pip install -r requirements.txt
    ```

2. **Generate SSL Certificates:**
    Example command:
    ```bash
    openssl req -new -x509 -days 365 -nodes -out server.crt -keyout server.key
    ```

3. **Database Initialization:**
    - Create the SQL database file.
    - Create the user table with the described structure.
    - Add at least 2 users to the table

4. **Run Server:**
    ```bash
    python server.py
    ```

5. **Run Client:**
    ```bash
    python client.py
    ```


## How it Works 📑

1. **SSL/TLS Connection:**  
   The client connects securely to the server using SSL/TLS.

2. **AES Encryption:**  
   Data sent after the initial handshake is encrypted with the AES algorithm.

3. **Database Management:**  
   Server handles user authentication and financial operations through SQL queries.

4. **User Operations:**  
   Clients can securely log in, check balances, and perform simple transactions asynchronously.

## Security Considerations 🚔
- All communications are encrypted via SSL/TLS and AES.
- Passwords are stored securely (optionally hashed and/or encrypted).
- Sensitive information is never transmitted in plain text.

