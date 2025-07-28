# pharma_chain/cli.py

import socket
import json
import os
import sys
from datetime import datetime
from utils import register_node
from blockchain import Blockchain, Block
import hashlib

UNIT_DIR = "units"
if not os.path.exists(UNIT_DIR):
    os.makedirs(UNIT_DIR)

def generate_unit_ids(batch_id, quantity):
    unit_ids = [f"{batch_id}_UID{str(i+1).zfill(4)}" for i in range(quantity)]
    with open(f"{UNIT_DIR}/{batch_id}_units.json", 'w') as f:
        json.dump(unit_ids, f, indent=4)
    return unit_ids

def calculate_unit_hash(unit_ids):
    sorted_units = sorted(unit_ids)
    joined = ''.join(sorted_units)
    return hashlib.sha256(joined.encode()).hexdigest()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python cli.py <role> <port>")
        sys.exit(1)

    role = sys.argv[1].lower()
    port = int(sys.argv[2])
    node_id = hex(hash((role, port)) & 0xffffffff)[2:]

    same_peers, other_peers = register_node('127.0.0.1', port, role, node_id)
    all_peers = same_peers + other_peers
    peer_addresses = [(peer['ip'], peer['port']) for peer in all_peers]

    blockchain = Blockchain(node_id)

    while True:
        cmd = input("\nType 'new' to add a new batch, 'receipt' to confirm a batch, or 'exit': ").strip().lower()

        if cmd == 'exit':
            break

        elif cmd == 'new':
            if role != 'manufacturer':
                print("[ERROR] Only manufacturers can create new batches.")
                continue

            batch_id = input("Batch ID: ")
            manufacturer = input("Manufacturer: ")
            drug_name = input("Drug Name: ")
            quantity = int(input("Quantity (number of units): "))
            mfg_date = input("Manufacture Date (YYYY-MM-DD): ")
            expiry_date = input("Expiry Date (YYYY-MM-DD): ")

            unit_ids = generate_unit_ids(batch_id, quantity)
            unit_hash = calculate_unit_hash(unit_ids)

            latest = blockchain.get_latest_block()
            new_block = Block(
                index=latest.index + 1,
                timestamp=datetime.utcnow(),
                batch_id=batch_id,
                manufacturer=manufacturer,
                drug_name=drug_name,
                quantity=quantity,
                mfg_date=mfg_date,
                expiry_date=expiry_date,
                previous_hash=latest.hash,
                unit_hash=unit_hash,
                creator_id=node_id
            )
            blockchain.add_block(new_block)
            print(f"\n✅ Block created and saved locally for batch {batch_id}")
            print(f"📦 Units saved in: {UNIT_DIR}/{batch_id}_units.json")
            print(f"🔍 Sample Unit ID: {unit_ids[0]}")

        elif cmd == 'receipt':
            batch_id = input("Batch ID to confirm receipt: ")
            action = input("Action (received/forwarded/sold): ").strip().lower()
            timestamp = datetime.utcnow()

            # Create a tracking block (no new units)
            latest = blockchain.get_latest_block()
            new_block = Block(
                index=latest.index + 1,
                timestamp=timestamp,
                batch_id=batch_id,
                manufacturer=f"{role}-{action}",
                drug_name="Tracking",
                quantity=0,
                mfg_date="N/A",
                expiry_date="N/A",
                previous_hash=latest.hash,
                unit_hash=None,
                creator_id=node_id
            )
            blockchain.add_block(new_block)
            print(f"\n✅ {role.capitalize()} logged action '{action}' for batch {batch_id}")

        else:
            print("[ERROR] Unknown command.")

        # Propagate to peers
        last_block = blockchain.get_latest_block()
        for addr in peer_addresses:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect(addr)
                    s.sendall(json.dumps({"type": "BLOCK", "block": last_block.to_dict()}).encode())
                    print(f"[PROPAGATED] Sent to {addr}")
            except Exception as e:
                print(f"[ERROR] Could not send to {addr}: {e}")
