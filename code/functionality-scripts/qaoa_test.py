import networkx as nx
import numpy as np
from qiskit_optimization import QuadraticProgram
from qiskit import Aer
from qiskit.algorithms import QAOA
from qiskit.algorithms.optimizers import COBYLA
from qiskit_optimization.translators import from_docplex_mp
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qiskit.primitives import Sampler

# -------------------------
# Step 1: Define Arbitrage Graph in NetworkX
# -------------------------
G = nx.DiGraph()

# Example edges (Token A to Token B with arbitrage profit weight)
edges = [
    ('A', 'B', 0.03), ('B', 'C', 0.05), ('C', 'A', 0.02),
    ('A', 'C', 0.01), ('C', 'B', -0.01)
]
G.add_weighted_edges_from(edges)

# Extract edge list and weights
edge_list = list(G.edges)
weights = np.array([G[u][v]['weight'] for u, v in edge_list])

# Number of edges
num_edges = len(edge_list)

# -------------------------
# Step 2: Define QUBO Problem
# -------------------------
qubo = QuadraticProgram()

# Add binary variables for each edge
for i, edge in enumerate(edge_list):
    qubo.binary_var(name=f"x_{i}")

# Objective Function: Maximize arbitrage profit (Minimize negative profit)
linear_coeffs = -weights  # Negate since QAOA minimizes
qubo.minimize(linear=linear_coeffs)

# Constraints: Flow Conservation (Each node must have in-degree = out-degree)
for node in G.nodes:
    in_edges = [i for i, (u, v) in enumerate(edge_list) if v == node]
    out_edges = [i for i, (u, v) in enumerate(edge_list) if u == node]

    constraint_expr = {f"x_{i}": 1 for i in in_edges}
    constraint_expr.update({f"x_{i}": -1 for i in out_edges})

    qubo.linear_constraint(
        linear=constraint_expr,
        sense='==',
        rhs=0,
        name=f"flow_{node}"
    )

# Print QUBO formulation
print("\nQUBO Formulation:\n", qubo.export_as_lp_string())

# -------------------------
# Step 3: Solve Using QAOA in Qiskit
# -------------------------
# Convert QuadraticProgram to Qiskit's QUBO format
qubo_operator = from_docplex_mp(qubo)

# Define QAOA with Quantum Simulator
sampler = Sampler()
qaoa = QAOA(sampler, optimizer=COBYLA(), reps=2)

# Solve using Minimum Eigen Optimizer
optimizer = MinimumEigenOptimizer(qaoa)
result = optimizer.solve(qubo_operator)

# -------------------------
# Step 4: Extract Results
# -------------------------
print("\nOptimal Arbitrage Cycle (Binary Representation):", result.x)
print("Optimized Profit:", -result.fval)  # Negate since we minimized

# Convert binary results to actual arbitrage cycle
selected_edges = [edge_list[i] for i in range(num_edges) if result.x[i] == 1]

print("\nArbitrage Cycle:", selected_edges)

# -------------------------
# Step 5: Run on Real Quantum Computer (Optional)
# -------------------------

# To execute on a real IBM quantum device:

# from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
# service = QiskitRuntimeService(channel="ibm_quantum")
# sampler = SamplerV2(service=service, backend="ibmq_qasm_simulator")
# qaoa = QAOA(sampler, optimizer=COBYLA(), reps=3)
# optimizer = MinimumEigenOptimizer(qaoa)
# result = optimizer.solve(qubo_operator)
