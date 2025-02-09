import os
import json
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv
from web3 import Web3, AsyncWeb3, AsyncHTTPProvider
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Load environment variables
load_dotenv()
FLARE_RPC_URL = os.getenv("FLARE_RPC_URL", "https://coston2-api.flare.network/ext/C/rpc")
ETH_RPC_URL = os.getenv("ETH_RPC_URL", "https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID")
AAVE_POOL = os.getenv("AAVE_POOL", "0xYourAaveTestnetPoolAddress")
DEPLOYER_PRIVATE_KEY = os.getenv("DEPLOYER_PRIVATE_KEY")

# Initialize Web3 Clients
web3_flare = AsyncWeb3(AsyncHTTPProvider(FLARE_RPC_URL))
web3_eth = Web3(Web3.HTTPProvider(ETH_RPC_URL))

def load_qaoa_trades():
    """Load the latest QAOA-selected trades."""
    try:
        with open("qaoa_trades.json", "r") as file:
            trades = json.load(file)
        return trades
    except FileNotFoundError:
        logging.warning("No QAOA trade file found.")
        return []

def check_profitability(trades):
    """Filter profitable trades."""
    return [trade for trade in trades if trade["expected_profit"] > 0]

def execute_flash_loan(trades):
    """Deploy contract and execute flash loans for profitable trades."""
    deployer = web3_eth.eth.account.from_key(DEPLOYER_PRIVATE_KEY)
    flash_loan_contract = web3_eth.eth.contract(address=AAVE_POOL, abi=json.loads(os.getenv("AAVE_ABI", "[]")))

    for trade in trades:
        asset = trade["asset"]
        amount = trade["amount"]

        tx = flash_loan_contract.functions.flashLoan(asset, amount).transact({"from": deployer.address})
        logging.info(f"Executed trade: {trade['pair']} | Expected Profit: {trade['expected_profit']}")
        log_trade(trade, tx)

def log_trade(trade, transaction):
    """Log trade execution details."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "trade": trade,
        "tx_hash": transaction.hex(),
    }
    with open("trade_log.json", "a") as file:
        json.dump(log_entry, file)
        file.write("\n")

def main():
    logging.info(f"Using Ethereum RPC: {ETH_RPC_URL}")
    logging.info(f"Using Flare RPC: {FLARE_RPC_URL}")
    trades = load_qaoa_trades()
    profitable_trades = check_profitability(trades)
    if profitable_trades:
        execute_flash_loan(profitable_trades)
    else:
        logging.info("No profitable trades found.")

if __name__ == "__main__":
    main()
