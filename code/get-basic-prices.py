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
FEED_IDS = [
    "0x01464c522f55534400000000000000000000000000",  # FLR/USD
    "0x014254432f55534400000000000000000000000000",  # BTC/USD
    "0x014554482f55534400000000000000000000000000",  # ETH/USD
]


# Ensure ABI is fully copied (not truncated)
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
