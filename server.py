import sys
import time
from socket import *

HEARTBEAT_TIMEOUT = 3
active_users = {}
credentials = {}
published_files = {}

if len(sys.argv) != 2:
    print("\n===== Error usage, python3 server.py SERVER_PORT ======\n")
    exit(0)

SERVER_HOST = "127.0.0.1"
SERVER_PORT = int(sys.argv[1])
SERVER_ADDRESS = (SERVER_HOST, SERVER_PORT)

server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind(SERVER_ADDRESS)


def load_credentials():
    global credentials
    with open('server/credentials.txt', 'r') as file:
        for line in file:
            username, password = line.strip().split()
            credentials[username] = password


def handle_client_message(message, client_address):
    commands = {
        'auth': authenticate,
        'heartbeat': handle_heartbeat,
        'get': get_file,
        'lap': list_active_peers,
        'lpf': list_published_files,
        'pub': publish_file,
        'sch': search_files,
        'unp': unpublish_file,
        'xit': disconnect_user
    }

    message_parts = message.split()
    command = message_parts[0]
    handler = commands.get(command)

    if handler:
        return handler(message_parts, client_address)

    return "Invalid command."


def authenticate(message_parts, client_address):
    username = message_parts[1]
    password = message_parts[2]
    tcp_port = int(message_parts[3])

    if username not in credentials:
        return "Unknown username"
    if credentials[username] != password:
        return "Password does not match"
    if username in active_users:
        return "User already active"

    active_users[username] = {
        'address': client_address,
        'tcp_port': tcp_port,
        'last_heartbeat': time.time()
    }

    print(f"===== New connection created for: {client_address}")

    for owners in published_files.values():
        if username in owners:
            owners[username] = True

    return "Authentication Success"


def handle_heartbeat(_, client_address):
    username = get_username(client_address)
    active_users[username]['last_heartbeat'] = time.time()


def is_user_active(username):
    last_heartbeat = active_users[username]['last_heartbeat']
    return time.time() - last_heartbeat <= HEARTBEAT_TIMEOUT


def get_file(message_parts, client_address):
    requested_file = message_parts[1]
    requesting_user = get_username(client_address)

    if requested_file in published_files:
        for owner in published_files[requested_file]:
            if owner in active_users and owner != requesting_user and is_user_active(owner):
                peer_address = active_users[owner]['address']
                peer_port = active_users[owner]['tcp_port']
                return f"{peer_address[0]} {peer_port}"

    return "File not found"


def list_active_peers(_, client_address):
    requesting_user = get_username(client_address)
    peers = [user for user in active_users if user != requesting_user]
    peers_count = len(peers)

    if peers:
        return f"{peers_count} active peer{'s' if peers_count > 1 else ''}:\n" + '\n'.join(peers)

    return "No active peers"


def list_published_files(_, client_address):
    requesting_user = get_username(client_address)
    user_files = [filename for filename, owners in published_files.items()
                    if requesting_user in owners and owners[requesting_user]]
    files_count = len(user_files)

    if user_files:
        return f"{files_count} file{'s' if files_count > 1 else ''} published:\n" + '\n'.join(user_files)

    return "No published files"


def publish_file(message_parts, client_address):
    filename = message_parts[1]
    username = get_username(client_address)

    if filename not in published_files:
        published_files[filename] = {}
    published_files[filename][username] = True

    return "File published successfully"


def search_files(message_parts, client_address):
    substring = message_parts[1]
    requesting_user = get_username(client_address)

    matches = [
        filename for filename, owners in published_files.items()
        if substring in filename and
        all(owner != requesting_user for owner in owners) and
        any(is_active and owner in active_users for owner, is_active in owners.items())
    ]
    matches_count = len(matches)

    if matches:
        return f"{matches_count} file{'s' if matches_count > 1 else ''} found:\n" + '\n'.join(matches)

    return "No files found"


def unpublish_file(message_parts, client_address):
    filename = message_parts[1]
    username = get_username(client_address)

    if filename in published_files and username in published_files[filename]:
        del published_files[filename][username]

        if not published_files[filename]:
            del published_files[filename]
        return "File unpublished successfully"

    return "File unpublication failed"


def disconnect_user(_, client_address):
    username = get_username(client_address)

    for filename in published_files:
        if username in published_files[filename]:
            published_files[filename][username] = False

    del active_users[username]
    print(f"===== The user disconnected - {client_address}")
    return "Goodbye!"


def get_username(client_address):
    return next((user for user, details in active_users.items()
                if details['address'] == client_address), None)


load_credentials()

print("\n===== Server is running =====")
print("===== Waiting for connection request from clients...=====")

while True:
    message, client_address = server_socket.recvfrom(1024)
    response = handle_client_message(message.decode(), client_address)
    if response:
        server_socket.sendto(response.encode(), client_address)
