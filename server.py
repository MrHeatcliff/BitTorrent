# Server
import socket
import pickle
import hashlib
from pathlib import Path
import os
from threading import Thread

file_path = Path('./Brabbit.webp')
file_exists = file_path.is_file()
fileList = ["Brabbit.webp"]
PIECE_SIZE = 1024

def split_file_into_pieces(file_path, piece_size):
    if(file_exists):
        # get file size
        file_size = os.path.getsize(file_path)

        # count number of pieces
        num_pieces = file_size // piece_size
        if file_size % piece_size != 0:
            num_pieces += 1

        pieces = []
        piece_hashes = []

        with open(file_path, 'rb') as f:
            for i in range(num_pieces):
                # read data from file
                piece_data = f.read(piece_size)
                pieces.append(piece_data)

                # hashing
                piece_hash = hashlib.sha1(piece_data).digest()
                piece_hashes.append(piece_hash)

        return pieces, piece_hashes

def new_connection(addr, conn):
    while True:
        data = conn.recv(1024).decode()
        print("Receive from client: " + str(data))
        match data:
            case "GET LIST":
                conn.send(str(fileList).encode())
            case "DOWNLOAD":
                pieces, piece_hashes = split_file_into_pieces(file_path, PIECE_SIZE)
                # conn.send(pieces[0])
                for piece, piece_hash in zip(pieces, piece_hashes):
                    # data = pickle.dump((piece, piece_hash))
                    data = piece
                    conn.send(data)
                    # ack = conn.recv(1024)
                    # if ack != b'ACK':
                #         print("ERROR")
                #         break
                conn.send(b'#END')

            case _:
                conn.send("Received".encode())
        print(fileList)

def server_program(host, port):
    serversocket = socket.socket()
    serversocket.bind((host, port))

    serversocket.listen(10)
    while True: 
        conn, addr = serversocket.accept()
        nconn = Thread(target=new_connection, args=(addr, conn))
        nconn.start()

if __name__ == "__main__":
    host = "192.168.1.33"
    port = 22236
    server_program(host, port)