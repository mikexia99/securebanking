import socket
import sys
import rsa
import hashlib
import pickle

SERVER = sys.argv[1]
PORT = int(sys.argv[2])
FORMAT = "utf-8"
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket. SOCK_STREAM)
client.connect(ADDR)

def login():
    login_status = False
    while login_status == False:
        input_id = input("Please enter you id: ")
        input_password = input("Please enter your password: ")
        with open("public.pem", "rb") as myfile:
            public_key = rsa.PublicKey.load_pkcs1(myfile.read())

        encrypted_id = rsa.encrypt(input_id.encode(), public_key)
        encrypted_password = rsa.encrypt(input_password.encode(), public_key)

        login_info = pickle.dumps((encrypted_id, encrypted_password))
        client.send(login_info)
        reply = client.recv(2048).decode(FORMAT)
        if reply == "1":
            login_status = True
            exit = False
            
            while exit == False: 
                balance = client.recv(2048).decode(FORMAT)
                print("Your account balance is", balance, ". Please select one of the following: ")
                print("1. Deposit")
                print("2. Withdraw")
                print("3. Exit")
                command = input("Select: ")
                if command == "1":
                    client.send(command.encode(FORMAT))
                    amount = input("Enter the amount: ")

                    while not amount.isnumeric():
                        amount = input("Please enter a numeric value: ")
                    
                    client.send(amount.encode(FORMAT))
                    

                    while True:
                        reply = client.recv(2048).decode(FORMAT)
                        break

                elif command == "2":
                    client.send(command.encode(FORMAT))
                    amount = input("Enter the amount: ")

                    while not amount.isnumeric() or int(amount) > int(balance):
                        while not amount.isnumeric():
                            amount = input("Please enter a numeric value: ")
                        while int(amount) > int(balance):
                            amount = input("Insufficient fund to withdraw, please try again: ")
                    amount = "-" + amount
                    client.send(amount.encode(FORMAT))
                    while True:
                        reply = client.recv(2048).decode(FORMAT)
                        break
                            

                elif command == "3":
                    exit = True
                    client.send(command.encode(FORMAT))

                else:
                    print("Invalid command, please try again")
                    client.send("INVALI COMMAND".encode(FORMAT))
                
        else:
            print("Invalid id or password, please try again")


login()
client.close()
