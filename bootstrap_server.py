# pharma_chain/bootstrap_server.py

import socket
import threading
import json

clusters = {
    'manufacturer': [],
    'distributor': [],
    'pharmacy': []
}

lock = threading.Lock()

def handle_client(conn, addr):
    try:
        data = json.loads(conn.recv(4096).decode())
        ip = data['ip']
        port = data['port']
        role = data['role']
        node_id = data['node_id']

        node_info = {'ip': ip, 'port': port, 'id': node_id, 'role': role}

        with lock:
            if role not in clusters:
                clusters[role] = []
            cluster = clusters[role]
            if not any(n['id'] == node_id for n in cluster):
                cluster.append(node_info)

            # same-cluster peers
            neighbours = [n for n in cluster if n['port'] != port]

            # Optionally include all other clusters
            all_peers = [
                n for r, lst in clusters.items() if r != role for n in lst
            ]

        response = {
            'cluster_id': role,
            'neighbours': neighbours,
            'all_peers': all_peers
        }

        conn.sendall(json.dumps(response).encode())
        print(f"[REGISTER] {node_id} as {role} at {ip}:{port}")

    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        conn.close()

def start_bootstrap_server(host='127.0.0.1', port=8000):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    print(f"[BOOTSTRAP SERVER] Listening on {host}:{port}")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == '__main__':
    start_bootstrap_server()
