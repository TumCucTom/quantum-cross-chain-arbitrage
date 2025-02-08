import networkx as nx
import numpy as np
import pennylane as qml
from pennylane import numpy as pnp
from qiskit.algorithms.optimizers import COBYLA
from qiskit import Aer
import matplotlib.pyplot as plt

# -----------------------------
# 1️⃣ Build Arbitrage Graph
# -----------------------------

# Define liquidity pools (Example: ETH, USDT, FLR, BTC)
edges = [
    ("ETH", "USDT", 0.005),  # Example: ETH to USDT (0.5% slippage)
    ("USDT", "FLR", 0.003),  # USDT to FLR (0.3% slippage)
    ("FLR", "ETH", -0.007),  # FLR back to ETH (-0.7% profit)
    ("ETH", "BTC", 0.004),   # ETH to BTC
    ("BTC", "USDT", 0.006)   # BTC to USDT
]

# Create a directed graph
G = nx.DiGraph()
for src, dst, weight in edges:
    G.add_edge(src, dst, weight=weight)

# Draw the graph
plt.figure(figsize=(6, 4))
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_color="lightblue", edge_color="gray", node_size=3000, font_size=12)
edge_labels = {(src, dst): f"{weight*100:.2f}%" for src, dst, weight in edges}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
plt.title("Arbitrage Graph")
plt.show()

# -----------------------------
# 2️⃣ Quantum Approximate Optimization Algorithm (QAOA)
# -----------------------------

# Convert graph to adjacency matrix for quantum optimization
num_assets = len(G.nodes)
adj_matrix = np.zeros((num_assets, num_assets))
node_index = {node: i for i, node in enumerate(G.nodes)}

for src, dst, weight in edges:
    i, j = node_index[src], node_index[dst]
    adj_matrix[i][j] = weight

# Quantum device setup
dev = qml.device("default.qubit", wires=num_assets)

# QAOA Parameters
depth = 2  # Number of QAOA layers

def qaoa_circuit(gamma, beta):
    """QAOA Circuit for Arbitrage Optimization"""
    for i in range(num_assets):
        qml.Hadamard(wires=i)  # Apply Hadamard to all qubits

    # Apply phase separation
    for i in range(num_assets):
        for j in range(num_assets):
            if adj_matrix[i][j] != 0:
                qml.CNOT(wires=[i, j])
                qml.RZ(gamma * adj_matrix[i][j], wires=j)
                qml.CNOT(wires=[i, j])

    # Apply mixing Hamiltonian
    for i in range(num_assets):
        qml.RX(beta, wires=i)

# Define QAOA cost function
def cost_function(params):
    gamma, beta = params
    qaoa_circuit(gamma, beta)
    return qml.expval(qml.PauliZ(0))

# Optimize QAOA parameters using classical optimizer
optimizer = COBYLA()
initial_params = pnp.array([0.1, 0.1], requires_grad=True)
optimal_params = optimizer.optimize(num_vars=2, objective_function=cost_function, initial_point=initial_params)

print(f"Optimal QAOA Parameters: {optimal_params}")

# -----------------------------
# 3️⃣ Classical Path Optimization (Dijkstra's Algorithm)
# -----------------------------

def find_best_classical_path(G, start="ETH", end="USDT"):
    """Finds best arbitrage path using Dijkstra's Algorithm"""
    best_path = nx.shortest_path(G, source=start, target=end, weight="weight", method="dijkstra")
    total_cost = sum(G[u][v]["weight"] for u, v in zip(best_path, best_path[1:]))
    return best_path, total_cost

best_path, best_cost = find_best_classical_path(G)
print(f"Best Classical Arbitrage Path: {best_path} (Profitability: {best_cost*100:.2f}%)")

# -----------------------------
# 4️⃣ Compare Quantum vs Classical Optimization
# -----------------------------

# Print Results
print("\n🔹 Arbitrage Optimization Results 🔹")
print(f"Classical Best Path: {best_path} -> Profit: {best_cost*100:.2f}%")
print(f"Quantum-Optimized Arbitrage Parameters: {optimal_params}")

# Note: QAOA's optimized parameters will need to be converted to a real trading strategy.
