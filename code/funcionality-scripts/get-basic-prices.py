import json
import asyncio
import ssl
import certifi
from datetime import datetime
from web3 import AsyncHTTPProvider, AsyncWeb3
from typing import List, Tuple

# FtsoV2 address (Flare Testnet Coston2)
FTSOV2_ADDRESS = "0x3d893C53D9e8056135C26C8c638B76C8b60Df726"
RPC_URL = "https://coston2-api.flare.network/ext/C/rpc"

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

ABI_JSON_STRING = '''[
    {"inputs":[{"internalType":"address","name":"_addressUpdater","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},
    {"inputs":[],"name":"FTSO_PROTOCOL_ID","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"bytes21","name":"_feedId","type":"bytes21"}],"name":"getFeedById","outputs":[
        {"internalType":"uint256","name":"","type":"uint256"},
        {"internalType":"int8","name":"","type":"int8"},
        {"internalType":"uint64","name":"","type":"uint64"}
    ],"stateMutability":"payable","type":"function"}
]'''

# Convert ABI from JSON string to Python list
ABI = json.loads(ABI_JSON_STRING)

async def main() -> Tuple[List[int], List[int], int]:
    # Create SSL context using certifi
    ssl_context = ssl.create_default_context(cafile=certifi.where())

    # Initialize Web3 (without session)
    w3 = AsyncWeb3(AsyncHTTPProvider(RPC_URL))

    # Verify connection
    is_connected = await w3.is_connected()
    print("Web3 connection successful:", is_connected)

    if not is_connected:
        raise ConnectionError("Failed to connect to the Web3 provider.")

    # Set up contract instance (with valid ABI)
    ftsov2 = w3.eth.contract(address=w3.to_checksum_address(FTSOV2_ADDRESS), abi=ABI)

    # Fetch current feeds
    for feed_id in FEED_IDS:
        feeds, decimals, timestamp = await ftsov2.functions.getFeedById(feed_id).call()

        # Print results
        print("Feed ID:", feed_id)
        print("Feeds:", feeds)
        print("Decimals:", decimals)
        print("Timestamp:", timestamp)

        data = feeds, decimals, timestamp
        process_feed_data(*data)
        print("-------")

def process_feed_data(feed: int, decimals: int, timestamp: int):
    real_price = feed / (10 ** decimals)
    human_time = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')
    print(f"Actual Price: {real_price} USD")
    print(f"Timestamp: {human_time}")


if __name__ == "__main__":
    asyncio.run(main())
