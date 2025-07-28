# pharma_chain/utils.py

import socket
import json

def register_node(ip, port, role, node_id, bootstrap_ip='127.0.0.1', bootstrap_port=8000):
    data = {
        'ip': ip,
        'port': port,
        'role': role,
        'node_id': node_id
    }
    try:
        with socket.create_connection((bootstrap_ip, bootstrap_port)) as sock:
            sock.sendall(json.dumps(data).encode())
            response = sock.recv(4096)
            peers = json.loads(response.decode())
            print(f"[REGISTERED] {node_id} - {ip}:{port} as {role} in cluster {peers['cluster_id']}")
            return peers['neighbours'], peers['all_peers']
    except Exception as e:
        print(f"[ERROR] Could not register with bootstrap server: {e}")
        return [], []
