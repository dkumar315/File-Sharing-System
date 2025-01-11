import os
import sys
import time
import threading
from socket import *

if len(sys.argv) != 2:
    print("\n===== Error usage, python3 client.py SERVER_PORT ======\n")
    exit(0)

SERVER_HOST = "127.0.0.1"
SERVER_PORT = int(sys.argv[1])
SERVER_ADDRESS = (SERVER_HOST, SERVER_PORT)

client_socket = socket(AF_INET, SOCK_DGRAM)
client_username = None
running = True


def start_tcp_listener():
    tcp_socket = socket(AF_INET, SOCK_STREAM)
    tcp_socket.bind(('', 0))
    tcp_socket.listen()

    tcp_port = tcp_socket.getsockname()[1]
    threading.Thread(target=listen_for_incoming_requests, args=(tcp_socket,), daemon=True).start()

    return tcp_port


def listen_for_incoming_requests(tcp_socket):
    while True:
        conn, addr = tcp_socket.accept()
        threading.Thread(target=handle_file_transfer, args=(conn, addr), daemon=True).start()


def handle_file_transfer(conn, addr):
    requested_filename = conn.recv(1024).decode()
    file_path = os.path.join(client_username, requested_filename)

    if os.path.isfile(file_path):
        with open(file_path, 'rb') as file:
            while (chunk := file.read(1024)):
                conn.send(chunk)
    else:
        conn.send("File not found".encode())

    conn.close()


def authenticate():
    global client_username
    tcp_port = start_tcp_listener()

    while not client_username:
        username = input("Enter username: ").strip()
        password = input("Enter password: ").strip()

        if not username or not password:
            print("Invalid credentials. Please try again.")
            continue

        client_socket.sendto(f"auth {username} {password} {tcp_port}".encode(), SERVER_ADDRESS)
        response, _ = client_socket.recvfrom(1024)
        response = response.decode()

        if "Success" in response:
            client_username = username
            threading.Thread(target=send_heartbeat, daemon=True).start()
            print("Welcome to BitTrickle!")
        else:
            print(response)
            print("Authentication failed. Please try again.")


def send_heartbeat():
    global running
    while running and client_username:
        try:
            client_socket.sendto(f"heartbeat {client_username}".encode(), SERVER_ADDRESS)
            time.sleep(2)
        except OSError:
            break


def command_handler():
    global running
    while running:
        command = input("Available commands are: get, lap, lpf, pub, sch, unp, xit\n> ").strip()

        client_socket.sendto(command.encode(), SERVER_ADDRESS)
        response, _ = client_socket.recvfrom(1024)
        response = response.decode()

        if not command.startswith("get"):
            print(response)

        if command == "xit":
            running = False
            client_username = None
            client_socket.close()
            break
        elif command.startswith("get"):
            filename = command.split(" ", 1)[1]
            if response != "File not found":
                peer_ip, peer_port = response.split()
                download_file(peer_ip, int(peer_port), filename)
            else:
                print(response)


def download_file(peer_ip, peer_port, filename):
    peer_socket = socket(AF_INET, SOCK_STREAM)
    peer_socket.connect((peer_ip, peer_port))
    peer_socket.send(filename.encode())

    os.makedirs(client_username, exist_ok=True)
    file_path = os.path.join(client_username, filename)
    with open(file_path, 'wb') as file:
        while True:
            chunk = peer_socket.recv(1024)
            if chunk == b"File not found" or not chunk:
                break
            file.write(chunk)

    peer_socket.close()
    if os.path.isfile(file_path):
        print(f"{filename} downloaded successfully.")


if __name__ == "__main__":
    authenticate()
    if client_username:
        threading.Thread(target=command_handler).start()
