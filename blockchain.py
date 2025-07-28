# pharma_chain/blockchain.py

import hashlib
import json
import os
from datetime import datetime

BLOCKCHAIN_DIR = "blockchains"
if not os.path.exists(BLOCKCHAIN_DIR):
    os.makedirs(BLOCKCHAIN_DIR)

class Block:
    def __init__(self, index, timestamp, batch_id, manufacturer, drug_name,
                 quantity, mfg_date, expiry_date, previous_hash,
                 unit_hash=None, signature=None, creator_id=None, hash=None):
        self.index = index
        self.timestamp = timestamp if isinstance(timestamp, str) else timestamp.isoformat()
        self.batch_id = batch_id
        self.manufacturer = manufacturer
        self.drug_name = drug_name
        self.quantity = quantity
        self.mfg_date = mfg_date
        self.expiry_date = expiry_date
        self.previous_hash = previous_hash
        self.unit_hash = unit_hash
        self.signature = signature
        self.creator_id = creator_id
        self.hash = hash or self.calculate_hash()

    def calculate_hash(self):
        block_dict = {
            "index": self.index,
            "timestamp": self.timestamp,
            "batch_id": self.batch_id,
            "manufacturer": self.manufacturer,
            "drug_name": self.drug_name,
            "quantity": self.quantity,
            "mfg_date": self.mfg_date,
            "expiry_date": self.expiry_date,
            "previous_hash": self.previous_hash,
            "unit_hash": self.unit_hash,
            "creator_id": self.creator_id
        }
        block_string = json.dumps(block_dict, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(data):
        return Block(**data)

class Blockchain:
    def __init__(self, node_id):
        self.filename = os.path.join(BLOCKCHAIN_DIR, f"blockchain_{node_id}.json")
        self.chain = self.load_chain()

    def create_genesis_block(self):
        fixed_timestamp = "2025-01-01T00:00:00Z"
        return Block(
            index=0,
            timestamp=fixed_timestamp,
            batch_id="GENESIS",
            manufacturer="SYSTEM",
            drug_name="NONE",
            quantity=0,
            mfg_date="1970-01-01",
            expiry_date="1970-01-01",
            previous_hash="0"
        )

    def get_latest_block(self):
        return self.chain[-1]

    def is_valid_block(self, block):
        latest = self.get_latest_block()

        # 1. Block index must follow the previous
        if block.index != latest.index + 1:
            return False

        # 2. Block must reference correct previous hash
        known_hashes = [b.hash for b in self.chain]
        if block.previous_hash not in known_hashes:
            return False

        # 3. Block hash must match calculated hash
        if block.hash != block.calculate_hash():
            return False

        return True

    def add_block(self, block):
        if self.is_valid_block(block):
            self.chain.append(block)
            self.save_chain()
            return True
        return False

    def save_chain(self):
        with open(self.filename, 'w') as f:
            json.dump([b.to_dict() for b in self.chain], f, indent=4)

    def load_chain(self):
        if not os.path.exists(self.filename):
            return [self.create_genesis_block()]
        with open(self.filename, 'r') as f:
            data = json.load(f)
            return [Block.from_dict(b) for b in data]
