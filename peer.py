import tqdm
import os, threading, platform
import socket
import hashlib
from pathlib import Path

IP = '192.168.1.33'
PORT = 22236
ADDR = (IP, PORT)

PEER_SERVER_IP = '192.168.1.33'
PEER_SERVER_PORT = 11235

FORMAT = "utf-8"
SIZE = 1024
PEER_PATH = "./client_data"
PEER1_PATH = "./peer_data"
SERVER_DATA_PATH = "./server_data" #need define

if not os.path.exists(PEER_PATH):
    os.makedirs(PEER_PATH)

if not os.path.exists(SERVER_DATA_PATH):
    os.makedirs(SERVER_DATA_PATH)
PIECE_SIZE = 1024

client_list = []

def separate_string(data):
    data = data.replace("[", "")
    data = data.replace("]", "")
    data = data.replace("\'", "")
    data = data.replace(" ", "")
    splitData = data.split(",")
    for i in range(1, len(splitData), 2):
        splitData[i] = int(splitData[i])
    return splitData

def handlePconnect(conn, addr):
    print(f"Sender: {addr}")
    data = conn.recv(1024).decode()
    print(data)
    conn.send("Chuan bi nhan ne".encode())

    filename = conn.recv(1024).decode()
    filepath = os.path.join(SERVER_DATA_PATH, filename)
    pieces, piece_hashes = split_file_into_pieces(Path(filepath), PIECE_SIZE)
    for piece, piece_hash in zip(pieces, piece_hashes):
        data = piece
        conn.send(data)
    conn.send(b'#END')


def peer_client(host, port, filename):
    p_client = socket.socket()
    p_client.connect((host, port))

    mes = "Ok bro"
    p_client.send(mes.encode(FORMAT))
    print(p_client.recv(1024).decode())

    print(f"Receiver: {p_client.getsockname()}")

    p_client.send(filename.encode(FORMAT))

    filepath = os.path.join(PEER_PATH, filename)

    # start = p_client.recv(SIZE).decode(FORMAT)
    # mes, size = start.split('@')
    # p_client.send(mes.encode(FORMAT))
    
    # if mes == "Start downloading..":
    pieces = []
    piece_hashes =[]
    end = False
    while (not end):
        piece = p_client.recv(1024)
        if (b'#END' in piece):
            piece = piece[:-4]
            pieces.append(piece)
            end = True
            break
        pieces.append(piece)
    join_pieces(pieces, filepath)
    p_client.send("Finished Downloading.".encode(FORMAT))  

    
    

def peer_server(p_server):
    p_server.listen(10)

    while True:
        try:
            print("wait....")
            conn, addr = p_server.accept()
            print("connected")
            thrHandle = threading.Thread(target=handlePconnect, args=(conn, addr))
            thrHandle.start()
        except:
            print("Your connection is not successful.")
            break

def recv(client):
    while True:
        print("startloop")
        data = client.recv(SIZE).decode(FORMAT)
        cmd, msg = data.split("@")

        if cmd == "DISCONNECTED":
            print(f"[SERVER]: {msg}")
            break
        elif cmd == "OK":
            print(f"{msg}")
        elif cmd == "FIND":
            print(f"{msg}")
            filepath = os.path.join(SERVER_DATA_PATH, msg)

            if(os.path.exists(filepath)):
                client.send("YES".encode())

        elif cmd == "GIVE":
            print(f"{msg}")
            otherPeer = msg.split(",")

            peerName = otherPeer[0]
            peerName = peerName.replace("'", "")
            peerPort = int(otherPeer[1])
            
            print(peerName)
            print(peerPort)
            thrClient = threading.Thread(target=peer_client, args=(peerName, peerPort))
            thrClient.start()

def sen(client):
    while True:
        print("startloop")
        data = client.recv(SIZE).decode(FORMAT)
        print(data)
        data = data.split("@")
        cmd, msg = data[0], data[1]

        if cmd == "DISCONNECTED":
            print(f"[SERVER]: {msg}")
            break
        elif cmd == "OK":
            print(f"{msg}")
        elif cmd == "FIND":
            print(f"{msg}")
            filepath = os.path.join(SERVER_DATA_PATH, msg)

            if(os.path.exists(filepath)):
                client.send("YES".encode())
        elif cmd == "GIVE":
            print(f"{msg}")
            otherPeer = msg.split(",")

            peerName = otherPeer[0]
            peerName = peerName.replace("'", "")
            peerPort = int(otherPeer[1])
            
            print(peerName)
            print(peerPort)
            thrClient = threading.Thread(target=peer_client, args=(peerName, peerPort, data[2]))
            thrClient.start()
        data = input("> ")
        data = data.split(" ")
        cmd = data[0]

        if cmd == "HELP":
            client.send(cmd.encode(FORMAT))
        elif cmd == "LOGOUT":
            client.send(cmd.encode(FORMAT))
            break
        elif cmd == "PEERS":
            client.send(cmd.encode(FORMAT))
        elif cmd == "REQ":
            client.send(f"{cmd}@{data[1]}".encode(FORMAT))
        elif cmd == "LIST":
            client.send(cmd.encode(FORMAT))
        elif cmd == "DELETE":
            client.send(f"{cmd}@{data[1]}".encode(FORMAT))
        elif cmd == "UPLOAD":
            filename = data[1]
            send_data = f"{cmd}@{filename}"
            client.send(send_data.encode(FORMAT))
            
        elif cmd == "DOWNLOAD":
            filename = data[1]

            peerIp = data[2]
            peerport = data[3]
            client.send(f"{cmd}@{filename}:{peerIp} {peerport}".encode(FORMAT))
        else:
            print("pass")
            client.send("pass".encode())

        print("endloop")

    print("Disconnected from the server.")
    client.close()

def main():
    client_to_tracker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_to_tracker.connect(ADDR)
    message = "NOPE"
    p_server = socket.socket()
    p_server.bind((PEER_SERVER_IP, PEER_SERVER_PORT))
    print(p_server.getsockname())

    client_to_tracker.send(str(p_server.getsockname()).encode(FORMAT))
    ser = threading.Thread(target = peer_server, args = (p_server,))
    ser.start()

    sen(client_to_tracker)
    try:
        p_server.close()
    except:
        ser.join()
        print("Disconnected from the server.")        

def split_file_into_pieces(file_path, piece_size):
    file_path = Path(file_path)
    if(file_path.is_file()):
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

def join_pieces(pieces, output_file_path):
    # create file
    with open(output_file_path, 'wb') as new_file:
        for piece in pieces:
            # hash checking
            # if hashlib.sha1(piece).digest() != piece_hash:
            #     raise ValueError("Hash của piece không khớp với hash trong torrent file")

            # write data
            new_file.write(piece)    

if __name__ == "__main__":
    # filename = 'Brabbit.webp'
    # filepath = os.path.join(Path(SERVER_DATA_PATH), filename)
    # pieces, piece_hashes = split_file_into_pieces(filepath, PIECE_SIZE)
    # print(pieces)
    main()