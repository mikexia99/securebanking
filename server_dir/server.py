import socket
import sys
import rsa
import hashlib
import pickle

HOST = socket.gethostname()
PORT = int(sys.argv[1])
ADDR = (HOST, PORT)
FORMAT = "utf-8"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

def deposit(user_id):
    waiting = True
    while waiting:
        amount = conn.recv(2048).decode(FORMAT)
        if amount:
            data = []
            with open("balance.txt", "r+") as new_file:
                for line in new_file:
                    info = line.split()
                    if info[0] == user_id:
                        data.append((info[0], int(info[1]) + int(amount), "\n"))
                    else:
                        data.append((info[0], info[1], "\n"))

                new_file.seek(0)
                for d in data:
                    new_file.write(" ".join(str(x) for x in d))

                new_file.truncate()
                conn.send("1".encode(FORMAT))
                waiting = False

def handle_client(conn, addr):
    connected = True
    while connected:
        flag = False
        login_info = conn.recv(2048)

        if login_info:
            login_info = pickle.loads(login_info)

            with open("private.pem", "rb") as myfile:
                private_key = rsa.PrivateKey.load_pkcs1(myfile.read())

            decrypted_id = rsa.decrypt(login_info[0], private_key)
            decrypted_id = decrypted_id.decode()
            decrypted_password = rsa.decrypt(login_info[1], private_key)
            decrypted_password = decrypted_password.decode()

        
            with open("passwd.txt", "r") as f:
                for line in f:
                    client_id, client_password = line.split()
                    if decrypted_id == client_id:
                        if hashlib.md5(decrypted_password.encode()).hexdigest() == client_password:
                            conn.send("1".encode(FORMAT))

                            sending_deposit = True
                            while sending_deposit:
                                with open("balance.txt", "r") as balance_file:
                                    for balance_line in balance_file:
                                        balance_id, balance_balance = balance_line.split()
                                        if balance_id == decrypted_id:
                                            conn.send(balance_balance.encode(FORMAT))
                                            reply = conn.recv(2048).decode(FORMAT)
                                            if reply == "1" or reply == "2":
                                                deposit(balance_id)
                                            elif reply == "3":
                                                sending_deposit = False
                                                connected = False
                                            
                                            break
                                            

                        else:
                            conn.send("0".encode(FORMAT))
                        flag = True 
                        break

                if not flag:
                    conn.send("0".encode(FORMAT))

    conn.close()

server.listen()
while True:
    conn, addr = server.accept()
    handle_client(conn, addr)


