# deploy_flash_loan.py
import os
from ape import accounts, project

def main():
    """Deploy Flash Loan Arbitrage Contract and execute a flash loan."""

    # Load deployer account dynamically
    account_name = os.getenv("APE_DEPLOYER", "default_account")
    deployer = accounts.load(account_name)

    # Ensure sufficient balance
    if deployer.balance == 0:
        raise ValueError("Deployer has insufficient funds to deploy the contract.")

    # Deploy the contract
    try:
        contract = deployer.deploy(project.FlashLoanArbitrage)
        print(f"Contract Deployed at: {contract.address}")
    except Exception as e:
        print(f"Contract Deployment Failed: {e}")
        return

    # Configurable lending pool and token
    aave_pool = os.getenv("AAVE_POOL", "0x7d2768dE32b0b80b7a3454c06BdAc9FbFf95D10D")
    asset = os.getenv("DAI_ADDRESS", "0x6B175474E89094C44Da98b954EedeAC495271d0F")

    # Borrow amount (10,000 DAI)
    amount = int(os.getenv("LOAN_AMOUNT", 10_000 * 10**18))  # Default to 10k DAI

    # Execute the Flash Loan with error handling
    try:
        tx = contract.flashLoan(aave_pool, asset, amount)
        tx.wait_for_confirmation()
        print(f"Flash Loan Executed: {tx.txn_hash}")
    except Exception as e:
        print(f"Flash Loan Execution Failed: {e}")
