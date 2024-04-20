# from makeTorrent import makeTorrent
import tqdm
import os, threading, platform
import socket
import hashlib
from pathlib import Path

IP = "192.168.1.33" # 
PORT = 22236
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
SERVER_DATA_PATH = "server_data" #need define

client_list = []
client_ips = []
peer_has_file = []
file_list = {}

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    conn.send("OK@Welcome to the File Server.\nPress 'HELP' to show all command.".encode(FORMAT))
    while True:
        data = conn.recv(SIZE).decode(FORMAT)
        data = data.split("@")
        cmd = data[0]

        if cmd == "LIST":
            send_data = "OK@"
            if len(file_list) == 0:
                send_data += "There is no file for you to access."
            else:
                send_data += str(file_list)
            conn.send(send_data.encode(FORMAT))
        elif cmd == "YES":
            peer_has_file.append(conn)
        elif cmd == "PEERS":
            send_data = "OK@"
            send_data += str(client_ips)
            conn.send(send_data.encode(FORMAT))
        elif cmd == "REQ":
            print(len(client_list))
            for client in client_list:
                print(client)
                client.send(f"FIND@{data[1]}".encode(FORMAT))
                sock = client.recv(SIZE).decode(FORMAT)
                print(sock)
                if(sock == "YES"):
                    peer_has_file.append(client)
            print(peer_has_file)
            print(client_list)
            conn.send(f"GIVE@{client_ips[client_list.index(peer_has_file[0])]}".encode(FORMAT))
            
        elif cmd == "UPLOAD":
            filename = data[1]

            temp_list = file_list[client_ips[client_list.index(conn)]]
            temp_list.append(filename)

            file_list[client_ips[client_list.index(conn)]] = temp_list

            conn.send("OK@Server has received your file.".encode())

            print(file_list)

        elif cmd == "DOWNLOAD":
            rec_data = data[1]
            print(rec_data)
            rec_data = rec_data.split(":")
            print(rec_data)
            filename = rec_data[0]

            peername = rec_data[1]
            peername = peername.split(",")

            peerIp = peername[0]
            peerPort = peername[1]
            sender_server_id = client_ips.index(f"'{peerIp}',{peerPort}")
            sender = client_list[sender_server_id]

            sock = -1
            try:
                print(file_list[client_ips[sender_server_id]])
                sock = file_list[client_ips[sender_server_id]].index(filename)
            except:
                sock = -1
            if(sock < 0):
                conn.send(f"OK@There is no '{filename}' in {peername}".encode(FORMAT))
            else :
                conn.send(f"GIVE@{client_ips[client_list.index(sender)]}@{filename}".encode(FORMAT))

        elif cmd == "DELETE":
            files = os.listdir(SERVER_DATA_PATH)
            send_data = "OK@"
            filename = data[1]

            if len(files) == 0:
                send_data += "The server directory is empty"
            else:
                if filename in files:
                    if(platform.system() == "Linux"):
                        filepath = f"rm ./"
                    else:
                        filepath = f"del .\\"

                    filepath += os.path.join(SERVER_DATA_PATH, filename)

                    print(filepath)
                    os.system(filepath)
                    send_data += "File deleted successfully."
                else:
                    send_data += "File not found."

            conn.send(send_data.encode(FORMAT))

        elif cmd == "LOGOUT":
            break
        elif cmd == "HELP":
            data = "OK@"
            data += "LIST: List all peers and its file.\n"
            data += "PEERS: List all peers.\n"
            data += "REQ <file>: Find <file> and download it from 1 peer has it \n"
            data += "UPLOAD <filename>: Upload file to the server know you have it.\n"
            # data += "DOWNLOAD <path>: Download a file from  the server.\n"
            data += "DOWNLOAD <file> <peername>: Download <file> from <peername>.\n"
            # data += "DELETE <filename>: Delete a file from the server.\n"
            data += "LOGOUT: Disconnect from the server.\n"
            data += "HELP: List all the commands."

            conn.send(data.encode(FORMAT))
        else:
            conn.send("OK@metvl".encode())

    print(f"[DISCONNECTED] {addr} disconnected")
    client_list.remove(conn)
    conn.close()

def main():
    print("[STARTING] Server is starting")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[LISTENING] Server is listening on {IP}:{PORT}.")

    while True:
        conn, addr = server.accept()

        peerSocket = conn.recv(1024).decode(FORMAT)
        peerSocket = peerSocket.replace("(", "")
        peerSocket = peerSocket.replace(")", "")

        file_list[peerSocket] = []
        client_ips.append(peerSocket)
        client_list.append(conn)
        try:
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
        except:
            print("error")
            break

if __name__ == "__main__":
    main()