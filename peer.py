# Client
import socket
import pickle
import socket
from threading import Thread
from pathlib import Path

OUTPUT_FILE = Path("./new/newfile.webp")
myList = []
PEER_SERVER_IP = '192.168.1.33'
PEER_SERVER_PORT = 11234

def new_connection(addr, conn):
    data = conn.recv(1024).decode()
    print(data)
    conn.send("hello".encode())

def peer_server(host, port):
    peerServerSocket = socket.socket()
    peerServerSocket.bind((host, port))

    peerServerSocket.listen(10)
    while True:
        conn, addr = peerServerSocket.accept()
        nconn = Thread(target = new_connection, args = (addr, conn))
        nconn.start()

def peer_client(host, port):
    client_socket = socket.socket()
    client_socket.connect((host, port))
    message = "HELLO"
    client_socket.send(message.encode())
    client_socket.recv(1024).decode()

def separate_string(data):
    data = data.replace("[", "")
    data = data.replace("]", "")
    data = data.replace("\'", "")
    data = data.replace(" ", "")
    splitData = data.split(",")
    for i in range(1, len(splitData), 2):
        splitData[i] = int(splitData[i])
    return splitData

def join_pieces(pieces, output_file_path):
    # create file
    with open(output_file_path, 'wb') as new_file:
        for piece in pieces:
            # hash checking
            # if hashlib.sha1(piece).digest() != piece_hash:
                # raise ValueError("Hash của piece không khớp với hash trong torrent file")

            # write data
            new_file.write(piece) 

if __name__ == "__main__":
    host = "192.168.1.33"
    port = 22236
    client_socket = socket.socket()
    client_socket.connect((host, port))
    message = "NOPE"
    ser = Thread(target = peer_server, args = ((PEER_SERVER_IP, PEER_SERVER_PORT)))
    ser.start()
    while message.lower().strip() != "bye":
        match message:
            case "GET LIST":
                client_socket.send(message.encode())
                data = client_socket.recv(1024).decode()
                myList = separate_string(data)
                print(myList)
            case "DOWNLOAD":
                client_socket.send(message.encode())
                pieces = []
                piece_hashes =[]
                print("Downloading:", end="\n")
                end = False
                while (not end):
                    # piece = pickle.load(client_socket.recv(1024))
                    piece = client_socket.recv(1024)
                    if (b'#END' in piece):
                        # piece = piece.strip(b'#END')
                        end = True
                        break
                    pieces.append(piece)
                    # print('Piece:', piece)
                    # print('hash:', piece_hash)
                    # client_socket.send(b'ACK')
                join_pieces(pieces,OUTPUT_FILE)
                print("download complete")
            case _:
                client_socket.send(message.encode())
                data = client_socket.recv(1024).decode()
        message = input(" -> ")  # again take input
    client_socket.close()