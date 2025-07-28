# pharma_chain/verify_tool.py

import json
import os
import glob
import hashlib
from blockchain import Block

CHAIN_GLOB = os.path.join("blockchains", "blockchain_*.json")
UNIT_DIR = "units"

def load_all_chains():
    chains = []
    for file in glob.glob(CHAIN_GLOB):
        with open(file, 'r') as f:
            try:
                chain = json.load(f)
                chains.append((file, chain))
            except:
                print(f"[WARNING] Failed to read {file}")
    return chains

def calculate_unit_hash(unit_ids):
    sorted_units = sorted(unit_ids)
    joined = ''.join(sorted_units)
    return hashlib.sha256(joined.encode()).hexdigest()

def verify_unit(unit_id):
    if "_" not in unit_id:
        print("[ERROR] Invalid unit ID format (use BATCH001_UID0003)")
        return

    batch_id = unit_id.split("_")[0]
    unit_file = os.path.join(UNIT_DIR, f"{batch_id}_units.json")

    if not os.path.exists(unit_file):
        print(f"[NOT FOUND] No unit list found for batch: {batch_id}")
        return

    with open(unit_file, 'r') as f:
        units = json.load(f)

    if unit_id not in units:
        print(f"[INVALID] Unit ID '{unit_id}' is not part of batch '{batch_id}'")
        return

    expected_unit_hash = calculate_unit_hash(units)

    found = False
    for file, chain in load_all_chains():
        for block_data in chain:
            block = Block.from_dict(block_data)
            if block.batch_id == batch_id:
                found = True
                if block.unit_hash == expected_unit_hash:
                    print(f"\n✅ VERIFIED: Unit '{unit_id}' belongs to batch '{batch_id}'")
                    print(f"   - Found in blockchain file: {file}")
                    print(f"   - Manufacturer: {block.manufacturer}")
                    print(f"   - Drug: {block.drug_name}")
                    print(f"   - Expiry: {block.expiry_date}")
                    return
                else:
                    print(f"[WARNING] Unit hash mismatch in {file}")
                    return

    if not found:
        print(f"[NOT FOUND] Batch '{batch_id}' not found in any blockchain.")

if __name__ == '__main__':
    print("📦 PharmaChain Unit Verifier")
    while True:
        uid = input("\nEnter Unit ID to verify (e.g. BATCH001_UID0002 or 'exit'): ").strip()
        if uid.lower() == 'exit':
            break
        verify_unit(uid)
