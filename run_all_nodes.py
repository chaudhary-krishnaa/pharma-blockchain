# pharma_chain/run_all_nodes.py

import subprocess
import time

nodes = [
    ("manufacturer", 9001),
    ("manufacturer", 9002),
    ("distributor", 9003),
    ("distributor", 9004),
    ("pharmacy", 9005),
    ("pharmacy", 9006),
]

for role, port in nodes:
    subprocess.Popen(["python", "node.py", role, str(port)])
    print(f"Started {role} on port {port}")
    time.sleep(0.5)  # slight delay between launches

