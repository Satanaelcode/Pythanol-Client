import socket
import uuid
import threading
import sys

ADDRESS = ('_ftp._tcp.ethanol.rocks', 39997)

def read_address(data_input):
    address_length = data_input.read(1)[0]
    if address_length != 4 and address_length != 16:
        raise ValueError("Invalid IP-Address")
    address = data_input.read(address_length)
    port = int.from_bytes(data_input.read(2), byteorder='big')
    return (socket.inet_ntoa(address), port)

def main(args):
    if len(args) < 1:
        print("Usage: <ID:Key>", file=sys.stderr)
        return
    
    split = args[0].split(':')
    if len(split) != 2:
        print("Invalid format!", file=sys.stderr)
        return
    
    id = uuid.UUID(split[0])
    key = uuid.UUID(split[1])
    
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.connect(ADDRESS)
    local_address = sock.getsockname()

    sock.send(id.bytes)
    sock.send(key.bytes)
    
    status = sock.recv(1)[0]
    if status != 0:
        print(f"Failed with status code '{status}'!", file=sys.stderr)
        return
    
    target = read_address(sock.makefile('rb'))
    sock.close()
    
    print(f"Connecting to '{target}'...")
    new_sock = socket.socket()
    new_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    new_sock.bind(local_address)
    new_sock.connect(target)
    print("Successfully connected!")

    def send_messages():
        while True:
            message = input()
            new_sock.sendall((message + '\n').encode('utf-8'))

    threading.Thread(target=send_messages, daemon=True).start()

    reader = new_sock.makefile('r')
    while True:
        response = reader.readline()
        if response:
            print(response.strip())

if __name__ == '__main__':
    main(sys.argv[1:])
