import json
import asyncio
import ssl
import certifi
from datetime import datetime
from web3 import AsyncHTTPProvider, AsyncWeb3
from typing import List, Tuple
import networkx as nx
import numpy as np
import pennylane as qml
from pennylane import numpy as pnp
from qiskit_algorithms.optimizers import SPSA
import matplotlib.pyplot as plt

# -----------------------------
# 1️⃣ Fetch Real-Time Market Data (Flare FTSO V2)
# -----------------------------

# Flare Testnet Coston2 FTSO contract
FTSOV2_ADDRESS = "0x3d893C53D9e8056135C26C8c638B76C8b60Df726"
RPC_URL = "https://coston2-api.flare.network/ext/C/rpc"
FEED_IDS = {
    "FLR/USD": "0x01464c522f55534400000000000000000000000000",
    "BTC/USD": "0x014254432f55534400000000000000000000000000",
    "ETH/USD": "0x014554482f55534400000000000000000000000000"
}

# ABI for fetching feed data
ABI_JSON_STRING = '''[
    {"inputs":[{"internalType":"bytes21","name":"_feedId","type":"bytes21"}],"name":"getFeedById","outputs":[
        {"internalType":"uint256","name":"","type":"uint256"},
        {"internalType":"int8","name":"","type":"int8"},
        {"internalType":"uint64","name":"","type":"uint64"}
    ],"stateMutability":"payable","type":"function"}
]'''
ABI = json.loads(ABI_JSON_STRING)


async def fetch_market_data() -> dict:
    """Fetches live price data from Flare FTSO."""
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    w3 = AsyncWeb3(AsyncHTTPProvider(RPC_URL))

    if not await w3.is_connected():
        raise ConnectionError("Failed to connect to the Web3 provider.")

    ftsov2 = w3.eth.contract(address=w3.to_checksum_address(FTSOV2_ADDRESS), abi=ABI)
    market_data = {}

    for asset, feed_id in FEED_IDS.items():
        price, decimals, timestamp = await ftsov2.functions.getFeedById(feed_id).call()
        real_price = price / (10 ** decimals)
        human_time = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')
        market_data[asset] = real_price
        print(f"{asset}: {real_price} USD (Timestamp: {human_time})")

    return market_data

# -----------------------------
# 2️⃣ Build Arbitrage Graph with Live Data
# -----------------------------
def build_arbitrage_graph(market_data):
    """Builds an arbitrage graph with live exchange rates."""
    G = nx.DiGraph()

    # Define slippage estimates (can be adjusted based on liquidity)
    slippage = {
        ("ETH", "USDT"): 0.005,
        ("USDT", "FLR"): 0.003,
        ("FLR", "ETH"): -0.007,  # Negative means potential arbitrage profit
        ("ETH", "BTC"): 0.004,
        ("BTC", "USDT"): 0.006
    }

    # Convert market data into arbitrage weights
    exchange_rates = {
        ("ETH", "USDT"): market_data["ETH/USD"],
        ("BTC", "USDT"): market_data["BTC/USD"],
        ("FLR", "USD"): market_data["FLR/USD"],
    }

    # Add graph edges with real-time price impact
    for (src, dst), slip in slippage.items():
        rate = exchange_rates.get((src, dst), 1)  # Default to 1 if rate unavailable
        weight = np.log(rate) - slip  # Log transform for additivity
        G.add_edge(src, dst, weight=weight)

    return G


# -----------------------------
# 3️⃣ Quantum Approximate Optimization Algorithm (QAOA)
# -----------------------------
def run_qaoa(G):
    """Runs QAOA on the arbitrage graph to find optimal trading path."""
    num_assets = len(G.nodes)
    matrix_size = 2 ** num_assets  # Ensure the matrix is 2^n x 2^n
    adj_matrix = np.zeros((matrix_size, matrix_size))
    node_index = {node: i for i, node in enumerate(G.nodes)}

    for u, v, data in G.edges(data=True):
        i, j = node_index[u], node_index[v]
        adj_matrix[i][j] = data["weight"]

    dev = qml.device("default.qubit", wires=num_assets)
    depth = 3  # Optimized QAOA depth

    @qml.qnode(dev)
    def qaoa_circuit(gamma, beta):
        for i in range(num_assets):
            qml.Hadamard(wires=i)
        for i in range(num_assets):
            for j in range(num_assets):
                if adj_matrix[i][j] != 0:
                    qml.CNOT(wires=[i, j])
                    qml.RZ(gamma * adj_matrix[i][j], wires=j)
                    qml.CNOT(wires=[i, j])
        for i in range(num_assets):
            qml.RX(beta, wires=i)
        return qml.expval(qml.Hermitian(adj_matrix, wires=list(range(num_assets))))

    def cost_function(params):
        return -qaoa_circuit(params[0], params[1])

    optimizer = SPSA(maxiter=100)
    initial_params = pnp.array([0.1, 0.1], requires_grad=True)
    result = optimizer.minimize(fun=cost_function, x0=initial_params)
    optimal_params = result.x
    best_cost = result.fun

    print(f"\n🔹 Optimized QAOA Arbitrage Parameters:")
    print(f"Gamma: {optimal_params[0]:.4f}, Beta: {optimal_params[1]:.4f}")
    print(f"🔹 Expected Profitability: {-best_cost * 100:.2f}%")


# -----------------------------
# 4️⃣ Classical Path Optimization (Dijkstra)
# -----------------------------
def find_best_classical_path(G, start="ETH", end="USDT"):
    """Finds best arbitrage path using Dijkstra's Algorithm."""
    best_path = nx.shortest_path(G, source=start, target=end, weight="weight", method="dijkstra")
    total_cost = sum(G[u][v]["weight"] for u, v in zip(best_path, best_path[1:]))
    return best_path, total_cost


# -----------------------------
# 5️⃣ Run the Full Pipeline
# -----------------------------
async def main():
    market_data = await fetch_market_data()
    G = build_arbitrage_graph(market_data)

    # Run Quantum Optimization
    run_qaoa(G)

    # Run Classical Optimization
    best_path, best_cost = find_best_classical_path(G)
    print(f"\n🔹 Classical Best Arbitrage Path: {best_path} -> Profit: {best_cost * 100:.2f}%")


# Execute script
if __name__ == "__main__":
    asyncio.run(main())
