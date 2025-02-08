import networkx as nx
import matplotlib.pyplot as plt
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from web3 import Web3

# --- Configuration ---
INFURA_URL = "https://mainnet.infura.io/v3/8ba16afae1db46e19bd1b161fc9cc720"

# TheGraph API endpoint for Uniswap V3
UNISWAP_GRAPHQL_URL = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3"

# Token addresses (example: USDT, WETH, DAI)
TOKEN_ADDRESSES = {
    "USDT": "0xdac17f958d2ee523a2206206994597c13d831ec7",
    "WETH": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
    "DAI": "0x6b175474e89094c44da98b954eedeac495271d0f"
}

# --- Fetch Token Prices from Uniswap ---
def get_token_price_uniswap(token_address):
    """Fetch token price in ETH from Uniswap's latest subgraph"""

    # ✅ New Uniswap V3 Subgraph URL
    UNISWAP_GRAPHQL_URL = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3"

    transport = RequestsHTTPTransport(url=UNISWAP_GRAPHQL_URL)
    client = Client(transport=transport, fetch_schema_from_transport=False)

    query = gql(f"""
    {{
        token(id: "{token_address.lower()}") {{
            derivedETH
        }}
    }}
    """)

    try:
        result = client.execute(query)
        return float(result['token']['derivedETH'])  # Price in ETH
    except Exception as e:
        print(f"Error fetching token price for {token_address}: {e}")
        return None  # Return None if API fails


# --- Fetch Ethereum Gas Fees ---
def get_gas_fees():
    """Fetch live Ethereum gas price from Infura"""
    web3 = Web3(Web3.HTTPProvider(INFURA_URL))
    gas_price = web3.eth.gas_price  # in Wei
    gas_limit = 21000  # Minimum for simple transaction
    eth_fee = gas_price * gas_limit / 1e18  # Convert Wei to ETH
    return eth_fee

# --- Calculate Slippage ---
def calculate_slippage(input_amount, token_reserve, eth_reserve):
    """Calculate slippage cost based on liquidity pool reserves"""
    expected_price = eth_reserve / token_reserve
    new_reserve_eth = eth_reserve - (input_amount * expected_price)
    new_reserve_token = token_reserve + input_amount
    executed_price = new_reserve_eth / new_reserve_token
    slippage = abs((executed_price - expected_price) / expected_price) * 100
    return slippage

# --- Build Arbitrage Graph ---
def build_arbitrage_graph():
    """Construct a weighted graph with arbitrage opportunities"""
    G = nx.DiGraph()

    # Fetch Prices for Tokens
    prices = {symbol: get_token_price_uniswap(addr) for symbol, addr in TOKEN_ADDRESSES.items()}

    # Assume synthetic liquidity reserves (replace with live data)
    liquidity_reserves = {
        ("USDT", "WETH"): (100000, 500),
        ("WETH", "DAI"): (500, 150000),
        ("DAI", "USDT"): (150000, 100000)
    }

    # Fetch gas fees
    gas_fee = get_gas_fees()

    # Add edges with weights based on profitability, slippage, and fees
    for (token1, token2), (reserve1, reserve2) in liquidity_reserves.items():
        profitability = prices[token2] / prices[token1] - 1
        slippage_cost = calculate_slippage(10, reserve1, reserve2)
        weight = profitability - (slippage_cost / 100) - gas_fee

        if weight > 0:  # Only add profitable trades
            G.add_edge(token1, token2, weight=round(weight, 5))

    return G

# --- Visualize Graph ---
def plot_arbitrage_graph(G):
    """Visualize arbitrage graph with weighted edges"""
    plt.figure(figsize=(8, 6))
    pos = nx.spring_layout(G)  # Layout for visualization
    edge_labels = {(u, v): f"{d['weight']:.5f}" for u, v, d in G.edges(data=True)}

    nx.draw(G, pos, with_labels=True, node_color="lightblue", edge_color="gray", node_size=3000, font_size=10)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)

    plt.title("Quantum Arbitrage Graph")
    plt.show()

# --- Main Execution ---
if __name__ == "__main__":
    arbitrage_graph = build_arbitrage_graph()
    plot_arbitrage_graph(arbitrage_graph)
