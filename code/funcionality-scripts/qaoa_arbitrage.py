from itertools import permutations
import json
import ssl
import certifi
import networkx as nx
import matplotlib.pyplot as plt
from web3 import AsyncHTTPProvider, AsyncWeb3, Web3
import requests
import numpy as np
from qiskit_optimization import QuadraticProgram
from qiskit import Aer
from qiskit.algorithms import QAOA
from qiskit.algorithms.optimizers import COBYLA
from qiskit_optimization.translators import from_docplex_mp
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qiskit.primitives import Sampler
import time
from ape import accounts, project
from web3 import Web3


# --- Configuration ---
FTSOV2_ADDRESS = "0x3d893C53D9e8056135C26C8c638B76C8b60Df726"
INFURA_URL = "https://mainnet.infura.io/v3/8ba16afae1db46e19bd1b161fc9cc720"  # Replace with your Infura key
UNISWAP_V2_ROUTER = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"  # Uniswap V2 Router
FLARE_RPC_URL = "https://coston2-api.flare.network/ext/C/rpc"
ETHERSCAN_GAS_API = "https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey=YOUR_ETHERSCAN_API_KEY"

# Uniswap V2 ABIs
UNISWAP_V2_ABI = json.loads('[{"constant":true,"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"}],"name":"getPair","outputs":[{"internalType":"address","name":"pair","type":"address"}],"payable":false,"stateMutability":"view","type":"function"}]')

UNISWAP_V2_PAIR_ABI = json.loads('[{"constant":true,"inputs":[],"name":"getReserves","outputs":[{"internalType":"uint112","name":"reserve0","type":"uint112"},{"internalType":"uint112","name":"reserve1","type":"uint112"},{"internalType":"uint32","name":"blockTimestampLast","type":"uint32"}],"payable":false,"stateMutability":"view","type":"function"}]')


TOKEN_ADDRESSES = {
    "AAVE": "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9",
    "ADA": "0x3ee2200efb3400fabb9aacf31297cbdd1d435d47",
    "ALGO": "0xf4E3fe15fe13Ee5A6EeB67F18d7A30Fb863Ce20f",
    "APT": "0x00312B3D7f39F63b15D5B2078F2862249B09338D",
    "ARB": "0x912CE59144191C1204E64559FE8253a0e49E6548",
    "ATOM": "0x0eb3a705fc54725037cc9e008bdede697f62f335",
    "AVAX": "0x1ce0c2827e2ef14d5c4f29a091d735a204794041",
    "BCH": "0x8ff795a6f4d97e7887c79bea79aba5cc76444adf",
    "BNB": "0xb8c77482e45f1f44de1745f52c74426c631bdd52",
    "BTC": "0x7130d2a12b9bcbfae4f2634d864a1ee1ce3ead9c",
    "DOGE": "0xba2ae424d960c26247dd6c32edc70b295c744c43",
    "DOT": "0x7083609fce4d1d8dc0c979aab8c869ea2c873402",
    "ETC": "0xdD2799Fc98C010D967ba0a95A1fe6DaB8C08cb97",
    "ETH": "0x2170ed0880ac9a755fd29b2688956bd959f933f8",
    "FIL": "0x0d8ce2a99bb6e3b7db580ed848240e4a0f9ae153",
    "FLR": "0xc1b23c67dffb267956736dbea4b3962fed05763a",
    "FTM": "0xad29abb318791d579433d831ed122afeaf29dcfe",
    "HBAR": "0xa43C7F27E36279645Bd1620070414e564ec291a9",
    "ICP": "0xc807acd80861edd471115d505f1d7f3bb1808969",
    "LINK": "0x514910771AF9Ca656af840dff83E8264EcF986CA",
    "LTC": "0x4338665cbb7b2485a8855a139b75d5e34ab0db94",
    "NEAR": "0x85f17cf997934a597031b2e18a9ab6ebd4b9f6a4",
    "QNT": "0x4a220e6096b25eadb88358cb44068a3248254675",
    "SHIB": "0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE",
    "SOL": "0x1f54638b7737193ffd86c19ec51907a7c41755d8",
    "UNI": "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984",
    "USDC": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
    "USDT": "0xdac17f958d2ee523a2206206994597c13d831ec7",
    "XLM": "0xba5fe23f8a3a24bed3236f05f2fcf35fd0bf0b5c",
    "XRP": "0x1d2f0da169ceb9fc7b3144628db156f3f6c60dbe",
}

TOKEN_ADDRESSES = {symbol: Web3.to_checksum_address(address) for symbol, address in TOKEN_ADDRESSES.items()}

FEED_IDS = {
    "AAVE": "0x01414156452f555344000000000000000000000000",
    "ADA": "0x014144412f55534400000000000000000000000000",
    "ALGO": "0x01414c474f2f555344000000000000000000000000",
    "APT": "0x014150542f55534400000000000000000000000000",
    "ARB": "0x014152422f55534400000000000000000000000000",
    "ATOM": "0x0141544f4d2f555344000000000000000000000000",
    "AVAX": "0x01415641582f555344000000000000000000000000",
    "BCH": "0x014243482f55534400000000000000000000000000",
    "BNB": "0x01424e422f55534400000000000000000000000000",
    "BTC": "0x014254432f55534400000000000000000000000000",
    "DOGE": "0x01444f47452f555344000000000000000000000000",
    "DOT": "0x01444f542f55534400000000000000000000000000",
    "ETC": "0x014554432f55534400000000000000000000000000",
    "ETH": "0x014554482f55534400000000000000000000000000",
    "FIL": "0x0146494c2f55534400000000000000000000000000",
    "FLR": "0x01464c522f55534400000000000000000000000000",
    "FTM": "0x0146544d2f55534400000000000000000000000000",
    "HBAR": "0x01484241522f555344000000000000000000000000",
    "ICP": "0x014943502f55534400000000000000000000000000",
    "LINK": "0x014c494e4b2f555344000000000000000000000000",
    "LTC": "0x014c54432f55534400000000000000000000000000",
    "NEAR": "0x014e4541522f555344000000000000000000000000",
    "QNT": "0x01514e542f55534400000000000000000000000000",
    "SHIB": "0x01534849422f555344000000000000000000000000",
    "SOL": "0x01534f4c2f55534400000000000000000000000000",
    "UNI": "0x01554e492f55534400000000000000000000000000",
    "USDC": "0x01555344432f555344000000000000000000000000",
    "USDT": "0x01555344542f555344000000000000000000000000",
    "XLM": "0x01584c4d2f55534400000000000000000000000000",
    "XRP": "0x015852502f55534400000000000000000000000000",
}

# Convert ABI from JSON string to Python list
ABI_JSON_STRING = '''[
    {"inputs":[{"internalType":"address","name":"_addressUpdater","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},
    {"inputs":[],"name":"FTSO_PROTOCOL_ID","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"bytes21","name":"_feedId","type":"bytes21"}],"name":"getFeedById","outputs":[
        {"internalType":"uint256","name":"","type":"uint256"},
        {"internalType":"int8","name":"","type":"int8"},
        {"internalType":"uint64","name":"","type":"uint64"}
    ],"stateMutability":"payable","type":"function"}
]'''
ABI = json.loads(ABI_JSON_STRING)


async def fetch_gas_fees():
    """Fetch live gas fees from Ethereum"""
    try:
        response = requests.get(ETHERSCAN_GAS_API)
        gas_data = response.json()
        gas_price_gwei = float(gas_data["result"]["ProposeGasPrice"])  # Gwei
        gas_price_eth = gas_price_gwei / 10**9  # Convert Gwei to ETH
        return gas_price_eth
    except Exception as e:
        print(f"⚠️ Failed to fetch gas fees: {e}")
        return 0.0002  # Default fallback gas price


async def estimate_bridge_fee(tokenA, tokenB):
    """Fetch live bridge fees using Stargate API"""
    try:
        response = requests.get("https://stargate.finance/api/bridge-fees")
        bridge_data = response.json()
        fee = bridge_data.get(f"{tokenA}-{tokenB}", {}).get("fee", 0)
        return float(fee)
    except Exception as e:
        print(f"⚠️ Failed to fetch bridge fees: {e}")
        return 0  # Default no bridge fee


async def fetch_ftso_prices():
    """Fetch live token prices from Flare FTSO."""
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    w3 = AsyncWeb3(AsyncHTTPProvider(FLARE_RPC_URL))

    if not await w3.is_connected():
        raise ConnectionError("Failed to connect to Flare network.")

    # Example FTSO contract interaction (mocked, needs ABI)
    prices = {}
    # Here, implement contract call to fetch actual FTSO prices.
    return prices


async def fetch_reserves(tokenA, tokenB, web3):
    """Fetch reserves from Uniswap V2 Pair Contract."""
    try:
        pair_contract = web3.eth.contract(address=Web3.to_checksum_address(TOKEN_ADDRESSES[tokenA]), abi=[])
        reserves = await pair_contract.functions.getReserves().call()
        return reserves
    except Exception as e:
        print(f"❌ Error fetching reserves for {tokenA}-{tokenB}: {str(e)}")
        return None


async def build_arbitrage_graph(prices, web3):
    """Construct arbitrage graph using real-time reserves, gas, and bridge costs"""
    G = nx.DiGraph()

    # Fetch gas fees
    gas_cost = await fetch_gas_fees()

    # Define trading pairs
    token_pairs = list(permutations(TOKEN_ADDRESSES.keys(), 2))

    for tokenA, tokenB in token_pairs:
        if tokenA in prices and tokenB in prices:
            # Estimate bridge fee
            bridge_cost = await estimate_bridge_fee(tokenA, tokenB)

            # Fetch reserves
            reserves = await fetch_reserves(tokenA, tokenB, web3)
            if reserves:
                reserveA, reserveB = reserves
            else:
                continue

            # Compute slippage cost
            slippage_cost = (abs((reserveB / reserveA) - (reserveB - 1000) / (reserveA + 1000))) * 100

            # Compute profitability
            profitability = prices[tokenB] / prices[tokenA] - 1

            # Compute final edge weight
            trade_size = 1000
            weight = profitability - (slippage_cost / 100) - (gas_cost / trade_size) - (bridge_cost / trade_size)

            if weight > 0:
                G.add_edge(tokenA, tokenB, weight=round(weight, 5))

    return G


def plot_arbitrage_graph(G):
    """Visualize arbitrage graph with weighted edges."""
    plt.figure(figsize=(8, 6))
    pos = nx.spring_layout(G, seed=42)
    edge_labels = {(u, v): f"{d['weight']:.5f}" for u, v, d in G.edges(data=True)}

    nx.draw(G, pos, with_labels=True, node_color="lightblue", edge_color="gray", node_size=2500, font_size=10)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
    plt.title("Live Arbitrage Graph (Including Gas & Bridge Costs)")
    plt.show()


async def graph():
    web3 = AsyncWeb3(AsyncHTTPProvider(INFURA_URL))
    prices = await fetch_ftso_prices()
    arbitrage_graph = await build_arbitrage_graph(prices, web3)
    #plot_arbitrage_graph(arbitrage_graph)
    return arbitrage_graph

G = graph()

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

# need to learn at what point this is profitable
# if -result.fval > 0:

# Convert binary results to actual arbitrage cycle
selected_edges = [edge_list[i] for i in range(num_edges) if result.x[i] == 1]

print("\nArbitrage Cycle:", selected_edges)

# -------------------------
# Step 5: Run on Real Quantum Computer
# -------------------------

# To execute on a real IBM quantum device:

# from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
# service = QiskitRuntimeService(channel="ibm_quantum")
# sampler = SamplerV2(service=service, backend="ibmq_qasm_simulator")
# qaoa = QAOA(sampler, optimizer=COBYLA(), reps=3)
# optimizer = MinimumEigenOptimizer(qaoa)
# result = optimizer.solve(qubo_operator)

# Load contract and Web3
deployer = accounts.load("my_account")
contract = project.FlashLoanArbitrage.at("0xYourDeployedContractAddress")

def execute_flash_loan(trade):
    """Trigger Flash Loan Execution on-chain."""
    tokenA, tokenB, amount = trade
    tx = contract.execute_flash_loan("0xAaveLendingPoolAddress", tokenA, amount, sender=deployer)
    print(f"🚀 Executed Flash Loan for {amount} {tokenA} to trade with {tokenB}")
    return tx.txhash

def log_trade(trade, expected_profit, txhash, cross_chain_state_validated):
    """
    Log trade details to a JSON file, including Flare’s state validation result.
    """
    timestamp = time.time()
    log_entry = {
        "time": timestamp,
        "trade": trade,
        "expected_profit": expected_profit,
        "txhash": txhash,
        "cross_chain_state_validated": cross_chain_state_validated,
        "actual_profit": None  # Will be updated later
    }

    with open("trade_log.json", "a") as f:
        f.write(json.dumps(log_entry) + "\n")


def update_actual_profit(txhash, actual_profit):
    """Update the log file with the realized profit."""
    with open("trade_log.json", "r") as f:
        trades = [json.loads(line) for line in f]

    for trade in trades:
        if trade["txhash"] == txhash:
            trade["actual_profit"] = actual_profit
            break

    with open("trade_log.json", "w") as f:
        for trade in trades:
            f.write(json.dumps(trade) + "\n")


for trade in selected_edges:
    txhash = execute_flash_loan(trade)
    log_trade(trade, -result.fval, txhash)

def check_realized_profit(txhash, timestamp):
    """Fetch realized profit from the smart contract."""
    profit = contract.get_trade_profit(timestamp)
    update_actual_profit(txhash, profit)
    print(f"✅ Trade {txhash} realized profit: {profit}")

